erDiagram
    users {
        UUID uid PK "NOT NULL"
        VARCHAR username "NOT NULL"
        VARCHAR email "NOT NULL"
        VARCHAR first_name "NOT NULL"
        VARCHAR role "NOT NULL"
        BOOLEAN is_verified "NOT NULL"
        VARCHAR password_hash "NOT NULL"
        TIMESTAMP created_at "NOT NULL"
        TIMESTAMP updated_at "NOT NULL"
    }

    books {
        UUID uid PK "NOT NULL"
        VARCHAR title "NOT NULL"
        VARCHAR author "NOT NULL"
        INTEGER year "NOT NULL"
        INTEGER pages "NOT NULL"
        VARCHAR language "NOT NULL"
        TIMESTAMP created_at "NOT NULL"
        TIMESTAMP updated_at "NOT NULL"
        UUID user_id FK
    }

    reviews {
        UUID uid PK "NOT NULL"
        UUID book_id FK "NOT NULL"
        UUID user_id FK "NOT NULL"
        VARCHAR review_text
        INTEGER rating "NOT NULL"
        TIMESTAMP created_at "NOT NULL"
    }

    users ||--o{ books : "posts"
    users ||--o{ reviews : "writes"
    books ||--o{ reviews : "has"
  