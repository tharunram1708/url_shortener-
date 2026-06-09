CREATE DATABASE IF NOT EXISTS `url_shortener`
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE `url_shortener`;

CREATE TABLE IF NOT EXISTS `roles` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `role_name` VARCHAR(30) NOT NULL,
    UNIQUE KEY `uq_roles_role_name` (`role_name`),
    INDEX `ix_roles_role_name` (`role_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(150) NOT NULL,
    `password` VARCHAR(255) NOT NULL,
    `role_id` INT NOT NULL,
    UNIQUE KEY `uq_users_email` (`email`),
    INDEX `ix_users_email` (`email`),
    INDEX `ix_users_role_id` (`role_id`),
    CONSTRAINT `fk_users_role_id`
        FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `urls` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `original_url` VARCHAR(2048) NOT NULL,
    `short_code` VARCHAR(30) NOT NULL,
    `click_count` INT NOT NULL DEFAULT 0,
    `created_by` INT NOT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `uq_urls_short_code` (`short_code`),
    INDEX `ix_urls_short_code` (`short_code`),
    INDEX `ix_urls_created_by` (`created_by`),
    INDEX `ix_urls_original_url` (`original_url`(255)),
    CONSTRAINT `fk_urls_created_by`
        FOREIGN KEY (`created_by`) REFERENCES `users` (`id`)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `url_logs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `url_id` INT NOT NULL,
    `accessed_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `ip_address` VARCHAR(45),
    INDEX `ix_url_logs_url_id` (`url_id`),
    CONSTRAINT `fk_url_logs_url_id`
        FOREIGN KEY (`url_id`) REFERENCES `urls` (`id`)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `roles` (`role_name`)
VALUES ('admin'), ('user')
ON DUPLICATE KEY UPDATE `role_name` = VALUES(`role_name`);
