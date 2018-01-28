CREATE TABLE `strategy_runs`
(
    `id` VARCHAR(36) PRIMARY KEY NOT NULL,
    `run_at` INT NOT NULL,
    `market_name` VARCHAR(128) NOT NULL,
    `market_configuration` TEXT NOT NULL,
    `strategy_name` VARCHAR(128) NOT NULL,
    `strategy_configuration` TEXT NOT NULL,
    `interval_since` INT NOT NULL,
    `interval_till` INT,
    `candle_storage_name` VARCHAR(128) NOT NULL,
    `order_storage_name` VARCHAR(128) NOT NULL
);
