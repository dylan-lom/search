CREATE TABLE `pages` (
    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `path` TEXT NOT NULL,
    `title` TEXT NOT NULL
);

CREATE TABLE `pages_keywords` (
    `page` INTEGER NOT NULL REFERENCES `pages` (`id`),
    `keyword` TEXT NOT NULL,
    `score` INTEGER NOT NULL,
    PRIMARY KEY (`page`, `keyword`)
);
