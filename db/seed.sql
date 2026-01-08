-- Default admin user
-- Password: admin123 (CHANGE IN PRODUCTION!)
-- Hash generated with bcrypt (10 rounds)
INSERT INTO users (username, email, password, name, is_admin)
VALUES (
    'admin',
    'admin@gramatike.com',
    '$2a$10$rN8qN3K6zE3oX5J7uL8J1OeZ7R6P5K8vN9L3M2oP4Q6S8T0U2V4W6',
    'Administrator',
    1
);

-- Sample posts
INSERT INTO posts (user_id, content) VALUES
(1, 'Bem-vindo ao Gramátike v2! 🎓'),
(1, 'Projeto reconstruído do zero com foco em simplicidade.');
