CREATE TABLE IF NOT EXISTS dishes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  name TEXT NOT NULL UNIQUE,
  cooking_time INTEGER NOT NULL,
  description VARCHAR(140)
);

CREATE TABLE IF NOT EXISTS tags (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dish_tags (
  dish_id INTEGER NOT NULL,
  tag_id INTEGER NOT NULL,
  PRIMARY KEY (dish_id, tag_id),
  FOREIGN KEY (dish_id) REFERENCES dishes(id),
  FOREIGN KEY (tag_id) REFERENCES tags(id)
);

INSERT INTO 'tags' ('name') VALUES
  ('date night'),
  ('batch cooking'),
  ('weekday'),
  ('weekend');

INSERT INTO "dishes" ("name", "cooking_time", "description") VALUES
  ("Spaghetti Carbonara", 30, "A classic Italian pasta dish with a creamy sauce."),
  ("Spaghetti Al Crudo", 20, "Pasta dish with tomatoes, capers, olives, anchovies."),
  ("Vegetable Stir Fry", 20, "A quick and healthy dish with a variety of vegetables."),
  ("Chilli Con Carne", 70, "A spicy and flavorful dish with ground beef and beans."),
  ("Fish Fingers", 20, "A kid-friendly dish with breaded fish fillets."),
  ("Galettes", 30, "A French dish made with buckwheat flour and filled with savory ingredients."),
  ("Lentil, Tomato and Spinach Soup", 40, "A hearty and healthy soup with lentils, tomatoes, and spinach."),
  ("Green Waffles", 40, ""), -- cooking time?
  ("Vegetable Lasagne", 60, "A vegetarian version of the classic Italian dish with layers of pasta, vegetables, and cheese."),
  ("Duck Parmentier", 45, ""), -- cooking time?
  ("Homemade Pizzas", 100, ""), -- cooking time?
  ("Ratatouille", 60, ""), -- cooking time?
  ("Bacon and Pea Pasta", 35, "A simple and delicious pasta dish with bacon, peas, and Parmesan cheese."),
  ("Cherry Tomato and Sausage Bake", 75, "A flavorful and easy-to-make dish with cherry tomatoes, sausages, and herbs."),
  ("Aubergine Meatballs", 90, ""); -- ct?

INSERT INTO "dish_tags" ("dish_id", "tag_id") VALUES
  (1, 1),
  (2, 1),
  (15, 2);
