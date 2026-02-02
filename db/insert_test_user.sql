-- Test user: testuser / test@example.com / password: 123456
INSERT INTO users (username, email, password_hash, name, is_admin) 
VALUES ('testuser', 'test@example.com', '123456', 'Test User', 0);

-- Admin user: gramatike / admin@gramatike.com / password: gramatike2024
INSERT INTO users (username, email, password_hash, name, is_admin, role) 
VALUES ('gramatike', 'admin@gramatike.com', 'gramatike2024', 'Gramátike Admin', 1, 'admin');
