CREATE TABLE IF NOT EXISTS telegram_users (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL UNIQUE,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    language_code TEXT,
    is_bot BOOLEAN NOT NULL DEFAULT FALSE,
    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS quiz_sessions (
    id BIGSERIAL PRIMARY KEY,
    telegram_user_id BIGINT NOT NULL REFERENCES telegram_users(id) ON DELETE CASCADE,
    source TEXT NOT NULL DEFAULT 'QR_BUS_TEST',
    status TEXT NOT NULL DEFAULT 'started',
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ,
    score INTEGER NOT NULL DEFAULT 0,
    risk_label TEXT,
    energy_percent INTEGER,
    goal TEXT
);

CREATE INDEX IF NOT EXISTS idx_quiz_sessions_user_id ON quiz_sessions(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_quiz_sessions_started_at ON quiz_sessions(started_at);
CREATE INDEX IF NOT EXISTS idx_quiz_sessions_status ON quiz_sessions(status);

CREATE TABLE IF NOT EXISTS quiz_answers (
    id BIGSERIAL PRIMARY KEY,
    session_id BIGINT NOT NULL REFERENCES quiz_sessions(id) ON DELETE CASCADE,
    question_index INTEGER NOT NULL,
    question_tag TEXT NOT NULL,
    question_text TEXT NOT NULL,
    selected_options JSONB NOT NULL DEFAULT '[]'::jsonb,
    score INTEGER NOT NULL DEFAULT 0,
    answered_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (session_id, question_index)
);

CREATE INDEX IF NOT EXISTS idx_quiz_answers_session_id ON quiz_answers(session_id);

CREATE TABLE IF NOT EXISTS leads (
    id BIGSERIAL PRIMARY KEY,
    quiz_session_id BIGINT REFERENCES quiz_sessions(id) ON DELETE SET NULL,
    telegram_user_id BIGINT NOT NULL REFERENCES telegram_users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    source TEXT NOT NULL DEFAULT 'QR_BUS_TEST',
    status TEXT NOT NULL DEFAULT 'Новая заявка',
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    contact_time TEXT,
    assigned_to TEXT,
    next_action TEXT NOT NULL DEFAULT 'Позвонить / написать',
    next_contact_at TIMESTAMPTZ,
    call_result TEXT,
    admin_comment TEXT,
    concern TEXT,
    score INTEGER NOT NULL DEFAULT 0,
    risk_label TEXT,
    energy_percent INTEGER,
    complaints TEXT,
    last_tests TEXT,
    goal TEXT,
    telegram_username TEXT,
    telegram_id BIGINT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_telegram_id ON leads(telegram_id);

CREATE TABLE IF NOT EXISTS bot_events (
    id BIGSERIAL PRIMARY KEY,
    telegram_user_id BIGINT REFERENCES telegram_users(id) ON DELETE SET NULL,
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_bot_events_type ON bot_events(event_type);
CREATE INDEX IF NOT EXISTS idx_bot_events_created_at ON bot_events(created_at);
