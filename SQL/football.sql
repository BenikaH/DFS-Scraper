DROP TABLE IF EXISTS `rguru_stats`;
CREATE TABLE `rguru_stats`(
    id VARCHAR(5),
    name VARCHAR(30),
    week INT,
    dk_position VARCHAR(6),
    dk_pts DECIMAL(4,2),
    dk_salary INT,
    fd_position VARCHAR(6),
    fd_pts DECIMAL(4,2),
    fd_salary INT,
    team VARCHAR(3),
    opp VARCHAR(3),
    home_game CHAR(1));
CREATE INDEX id1 ON `rguru_stats`(id);