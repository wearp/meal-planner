import csv
import io
import os
import sqlite3

from typing_extensions import Annotated
from utils import send_email

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich import print


from openai import OpenAI

app = typer.Typer()
console = Console()

SENDER_EMAIL = "will.earp@icloud.com"
RECIPIENTS = [SENDER_EMAIL, "helpichon@gmail.com"]


@app.command(name="add-dish")
def add_dish(
    dish: str, cooking_time: int, description: Annotated[str, typer.Argument()]
):
    print(f"Adding dish: {dish}")
    connection = sqlite3.connect(os.getenv("DB_NAME"))
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO dishes VALUES (NULL, CURRENT_TIMESTAMP, ?, ?, ?)",
        (dish, cooking_time, description),
    )

    connection.commit()
    connection.close()


@app.command(name="delete-dish")
def delete_dish(dish: str):
    print(f"Deleting dish: {dish}")
    connection = sqlite3.connect(os.getenv("DB_NAME"))
    cursor = connection.cursor()

    cursor.execute("DELETE FROM dishes WHERE name = ?", (dish,))

    connection.commit()
    connection.close()


@app.command(name="list-dishes")
def list_dishes():
    dishes = _get_dishes()

    table = Table("Name", "Cooking Time (minutes)", "Description", "Tags")
    for row in dishes:
        table.add_row(row[0], str(row[1]), row[2], row[3])

    console.print(table)


def _get_dishes():
    connection = sqlite3.connect(os.getenv("DB_NAME"))
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT
            d.name AS dish_name,
            d.cooking_time,
            d.description,
            GROUP_CONCAT(t.name, ', ') AS tags
        FROM
            dishes d
        LEFT JOIN
            dish_tags dt ON d.id = dt.dish_id
        LEFT JOIN
            tags t ON dt.tag_id = t.id
        GROUP BY
            d.name, d.cooking_time, d.description;
        """
    )

    rows = cursor.fetchall()
    connection.close()

    return rows


@app.command(name="suggest-dishes")
def suggest(email: bool = typer.Option(False, "--send-email")):
    print("Suggesting dishes...")
    dishes = _get_dishes()

    output = io.StringIO()
    csv_writer = csv.writer(output)
    csv_writer.writerows(dishes)
    csv_string = output.getvalue()
    output.close()

    user_input = (
        "Choose a weekly menu from the comma-separated dishes below, "
        "considering the name, cooking time, description, and tags. Use the "
        '"General criteria" and "Days of the week criteria" bullet points for '
        "selection.\n\nOutput should be an email message body. It should:\n- "
        "Not include the subject line\n- Be plaintext (no Markdown, for "
        'example)\n- Be addressed to "Dear Parents"\n- Include a brief fun '
        "initial paragraph <30 words\n- Only include the name and cooking "
        'time (use word "minutes" in email) of each chosen dish\n- Sign-off '
        'should be "Sent with love from your happy household '
        'assistant"\n\nGeneral criteria:\n- Do not repeat dishes\n- Use tags '
        "(column 4) and description (column 3) to inform selection\n- "
        "Prioritise cooking time first, tags second, seasonal dishes "
        "third\n\nDays of the week criteria:\n- A week is Monday to Sunday\n- "
        "For Monday to Friday select a single dish. This dish is for "
        "dinner\n- For Monday and Friday cooking time should be 45 minutes "
        "or less\n- For Tuesday and Thursday cooking time should be 30 "
        "minutes or less\n- For Saturday and Sunday, select two dishes: one "
        "for lunch and dinner\n- For Saturday and Sunday lunch, cooking "
        "time should be 50 minutes or less\n- For Saturday and Sunday "
        "dinner, cooking time isn't a constraint for dinner\n- Saturday "
        'dinner should be a dish tagged "date night" \n- Do not chose '
        'dishes tagged "date night" for meals that are not Saturday '
        'dinner\n- Sunday should include one dish tagged '
        '"batch cooking"\n\nComma separated list of dishes:\n' + csv_string
    )
    system_input = (
        "You are a helpful household assistant for busy parents. Your "
        "speciality is planning an interesting range of tasty, seasonal "
        "dishes each week. You keep in mind that parents lead busy, "
        "stressful lives."
    )
    client = OpenAI(
        organization="org-CPJ1D5vxPzio5FzJrHRmE90F",
        project="proj_NGoVAyrUQFRIMTLjyUPNF2C0",
        api_key=os.getenv("PROJECT_OPENAI_API_KEY"),
    )

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "text": system_input,
                        "type": "text",
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_input,
                    }
                ],
            },
        ],
        temperature=1,
        max_tokens=500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "text"},
    )

    if email:
        try:
            print("Emailing suggestions...")
            send_email(
                sender_email=SENDER_EMAIL,
                recipients=["will.earp@icloud.com"],
                subject="Meal suggestions for week",
                body=completion.choices[0].message.content,
            )
        except Exception as e:
            print(f"Failed to send email: {e}")
    else:
        print(completion.choices[0].message.content)


@app.command(name="add-tag")
def add_tag(name: str):
    connection = sqlite3.connect(os.getenv("DB_NAME"))
    cursor = connection.cursor()

    cursor.execute("INSERT INTO tags VALUES (NULL, ?)", (name,))

    connection.commit()
    connection.close()

    print(f'Added tag "{name}" :green_check:')


@app.command(name="tag-dish")
def tag_dish(dish_name: str, tag_name: str):
    connection = sqlite3.connect(os.getenv("DB_NAME"))
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM dishes WHERE name = ?", (dish_name,))
    dish_id = cursor.fetchone()[0]
    cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
    tag_id = cursor.fetchone()[0]
    cursor.execute("INSERT INTO dish_tags VALUES (?, ?)", (dish_id, tag_id))

    connection.commit()
    connection.close()


@app.command(name="init-db")
def init_db():
    with open("schema.sql", "r") as schema_file:
        schema_script = schema_file.read()

    connection = sqlite3.connect(os.getenv("DB_NAME"))
    cursor = connection.cursor()

    cursor.executescript(schema_script)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    load_dotenv()
    app()
