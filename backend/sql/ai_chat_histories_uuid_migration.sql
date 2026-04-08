-- SQL Server migration for legacy ai_chat_histories integer columns.
-- Run once if the table was created before UUID/string IDs were adopted.

IF OBJECT_ID('dbo.ai_chat_histories', 'U') IS NOT NULL
AND EXISTS (
    SELECT 1
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = 'ai_chat_histories'
      AND COLUMN_NAME IN ('id', 'pet_id', 'user_id')
      AND DATA_TYPE NOT IN ('nvarchar', 'varchar', 'nchar', 'char', 'text', 'ntext')
)
BEGIN
    IF OBJECT_ID('dbo.ai_chat_histories_new', 'U') IS NOT NULL
        DROP TABLE dbo.ai_chat_histories_new;

    CREATE TABLE dbo.ai_chat_histories_new (
        id NVARCHAR(50) NOT NULL,
        pet_id NVARCHAR(50) NULL,
        user_id NVARCHAR(50) NULL,
        question NVARCHAR(MAX) NOT NULL,
        answer NVARCHAR(MAX) NOT NULL,
        created_at DATETIME2 NOT NULL CONSTRAINT DF_ai_chat_histories_new_created_at DEFAULT SYSDATETIME(),
        CONSTRAINT PK_ai_chat_histories_new PRIMARY KEY (id)
    );

    INSERT INTO dbo.ai_chat_histories_new (id, pet_id, user_id, question, answer, created_at)
    SELECT
        CAST(id AS NVARCHAR(50)),
        CAST(pet_id AS NVARCHAR(50)),
        CAST(user_id AS NVARCHAR(50)),
        question,
        answer,
        COALESCE(CAST(created_at AS DATETIME2), SYSDATETIME())
    FROM dbo.ai_chat_histories;

    IF OBJECT_ID('dbo.ai_chat_histories_legacy', 'U') IS NOT NULL
        DROP TABLE dbo.ai_chat_histories_legacy;

    EXEC sp_rename 'dbo.ai_chat_histories', 'ai_chat_histories_legacy';
    EXEC sp_rename 'dbo.ai_chat_histories_new', 'ai_chat_histories';

    DROP TABLE dbo.ai_chat_histories_legacy;
END