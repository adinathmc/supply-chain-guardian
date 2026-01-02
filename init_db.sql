CREATE TABLE products (
  product_id SERIAL PRIMARY KEY,
  product_name VARCHAR(255) NOT NULL,
  current_stock INTEGER NOT NULL DEFAULT 0,
  avg_daily_sale DECIMAL(10,2) DEFAULT 0.00,
  price_per_product DECIMAL(10,2) NOT NULL
);

INSERT INTO products (product_name, current_stock, avg_daily_sale, price_per_product) VALUES
('Organic Coffee Beans', 150, 5.5, 18.00),
('Premium Tea Leaves', 200, 12.2, 12.50),
('Cocoa Powder', 80, 3.1, 15.00),
('Vanilla Extract', 30, 0.8, 25.00);
