-- Stats
-- ['pt', 'rb', 'as', 'st', 'bl', 'to', 'trey', 'fg', 'ft']

DROP TABLE IF EXISTS `rguru_stats`;
CREATE TABLE `rguru_stats`(
    id VARCHAR(5),
    name VARCHAR(30),
    date DATE,
    dk_position VARCHAR(6),
    dk_pts DECIMAL(4,2),
    dk_salary INT,
    fd_position VARCHAR(6),
    fd_pts DECIMAL(4,2),
    fd_salary INT,
    team VARCHAR(3),
    opp VARCHAR(3),
    home_game CHAR(1),
    mins INT,
    pts INT,
    rb INT,
    asst INT,
    stl INT,
    blk INT,
    tovr INT,
    trey INT,
    fg_made INT,
    fg_att INT,
    ft_made INT,
    ft_att INT
);
CREATE INDEX id1 ON `rguru_stats` (id);
