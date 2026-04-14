-- =============================================================================
-- tg-story-bot database schema
-- PostgreSQL 14+
-- Only story-related tables and their dependencies are included.
-- =============================================================================

-- Core user table (referenced as FK by all story tables)
CREATE TABLE IF NOT EXISTS public.t_user (
    c_user_id         bigint PRIMARY KEY,
    c_subscription_status integer,
    c_balance         real,
    c_free_actions_count integer DEFAULT 0,
    c_free_actions_date  date,
    c_segment         text
);

-- Grammar rules (used for in-story grammar feedback)
CREATE TABLE IF NOT EXISTS public.t_grammar_block (
    c_id    integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    c_desc  text
);

CREATE TABLE IF NOT EXISTS public.t_grammar_weight (
    c_id    smallint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    c_desc  text
);

CREATE TABLE IF NOT EXISTS public.t_grammar (
    c_id      bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    c_ruleid  text NOT NULL UNIQUE,
    c_sdesc   text,
    c_ldesc   text,
    c_sdesc2  text,
    c_gr_block integer REFERENCES public.t_grammar_block(c_id) ON UPDATE CASCADE ON DELETE CASCADE,
    c_tech    text,
    c_msg     text,
    c_weight  smallint REFERENCES public.t_grammar_weight(c_id),
    c_tech3   text
);

-- =============================================================================
-- Story: reference tables
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.t_story_genre (
    c_id    integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    c_desc  text,
    c_emoji text
);

-- =============================================================================
-- Story: catalog
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.t_story_interactive_stories (
    c_story_id          integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    c_story_name        varchar(200) NOT NULL,
    c_description       text,
    c_genre             varchar(50),
    c_mood              varchar(50),
    c_realism           varchar(50),
    c_main_goal         varchar(50),
    c_grammar_context   varchar(200),
    c_difficulty_level  integer DEFAULT 1 CHECK (c_difficulty_level BETWEEN 1 AND 5),
    c_total_chapters    integer NOT NULL CHECK (c_total_chapters BETWEEN 1 AND 3),
    c_total_scenes      integer NOT NULL,
    c_estimated_minutes integer DEFAULT 15,
    c_story_skeleton    jsonb,        -- full JSON scene graph from AI
    c_generation_params jsonb,        -- genre/mood/complexity params used for generation
    c_story_elaboration jsonb,        -- detailed NPC knowledge and plot elaboration
    c_mystery_solution  jsonb,        -- what the story reveals at the end
    c_is_active         boolean DEFAULT true,
    c_is_public         boolean DEFAULT false,
    c_created_by_user_id bigint REFERENCES public.t_user(c_user_id) ON DELETE SET NULL,
    c_rating_avg        numeric(3,2) DEFAULT 0,
    c_times_completed   integer DEFAULT 0,
    c_times_started     integer DEFAULT 0,
    c_genre_id          integer REFERENCES public.t_story_genre(c_id),
    c_created_at        timestamp DEFAULT CURRENT_TIMESTAMP,
    c_updated_at        timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_story_active  ON public.t_story_interactive_stories (c_is_active);
CREATE INDEX idx_story_genre   ON public.t_story_interactive_stories (c_genre);
CREATE INDEX idx_story_public  ON public.t_story_interactive_stories (c_is_public, c_is_active);
CREATE INDEX idx_story_rating  ON public.t_story_interactive_stories (c_rating_avg DESC);

-- =============================================================================
-- Story: NPC characters
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.t_story_npcs (
    c_npc_id         integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    c_story_id       integer NOT NULL REFERENCES public.t_story_interactive_stories(c_story_id) ON DELETE CASCADE,
    c_name           varchar(100) NOT NULL,
    c_gender         varchar(10)  CHECK (c_gender IN ('male','female','neutral')),
    c_age_group      varchar(20)  CHECK (c_age_group IN ('young','middle','old')),
    c_personality    jsonb NOT NULL,  -- {traits: [...], base_mood: "..."}
    c_role_description text NOT NULL,
    c_goals          jsonb,           -- {primary: "...", secondary: [...]}
    c_appears_in_scenes jsonb,        -- array of scene_ids
    c_npc_role       varchar(20) DEFAULT 'companion'
                     CHECK (c_npc_role IN ('companion','local','antagonist','neutral')),
    c_voice          jsonb,           -- ["en-AU", "en-AU-Chirp-HD-D", "MALE"]
    c_voice_id       varchar(100),
    c_created_at     timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_npc_story ON public.t_story_npcs (c_story_id);

-- =============================================================================
-- Story: items / inventory
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.t_story_items (
    c_item_id       integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    c_story_id      integer NOT NULL REFERENCES public.t_story_interactive_stories(c_story_id) ON DELETE CASCADE,
    c_name          varchar(100) NOT NULL,
    c_name_trs      jsonb,
    c_description   text NOT NULL,
    c_purpose       text,
    c_initial_location varchar(100),
    c_location_type varchar(20) DEFAULT 'hidden'
                    CHECK (c_location_type IN ('hidden','npc','visible','inventory')),
    c_location_details    jsonb,
    c_acquisition_conditions jsonb,
    c_is_key_item   boolean DEFAULT false,
    c_created_at    timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_item_story ON public.t_story_items (c_story_id);

-- =============================================================================
-- Story: scenes (scene graph)
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.t_story_scenes (
    c_scene_id      integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    c_story_id      integer NOT NULL REFERENCES public.t_story_interactive_stories(c_story_id) ON DELETE CASCADE,
    c_chapter_number integer NOT NULL CHECK (c_chapter_number BETWEEN 1 AND 3),
    c_scene_number  integer NOT NULL,
    c_scene_name    varchar(200),
    c_scene_name_trs jsonb,
    c_location_description text NOT NULL,
    c_objective     text NOT NULL,
    c_objective_trs jsonb,
    c_npcs_present  jsonb,            -- array of npc_ids
    c_items_available jsonb,          -- array of item_ids
    c_success_conditions jsonb NOT NULL,  -- {type, target, keywords}
    c_detailed_objectives jsonb,      -- checklist of sub-objectives
    c_scene_context jsonb,            -- AI generation context
    c_next_scene_id integer REFERENCES public.t_story_scenes(c_scene_id) ON DELETE SET NULL,
    c_is_ending     boolean DEFAULT false,
    c_ending_type   varchar(50),
    c_created_at    timestamp DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (c_story_id, c_chapter_number, c_scene_number)
);

CREATE INDEX idx_scene_story   ON public.t_story_scenes (c_story_id);
CREATE INDEX idx_scene_chapter ON public.t_story_scenes (c_story_id, c_chapter_number);
CREATE INDEX idx_scene_ending  ON public.t_story_scenes (c_story_id, c_is_ending);

-- =============================================================================
-- Story: user session state
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.t_story_user_progress (
    c_progress_id      integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    c_user_id          bigint NOT NULL REFERENCES public.t_user(c_user_id) ON DELETE CASCADE,
    c_story_id         integer NOT NULL REFERENCES public.t_story_interactive_stories(c_story_id) ON DELETE CASCADE,
    c_current_scene_id integer NOT NULL REFERENCES public.t_story_scenes(c_scene_id) ON DELETE CASCADE,
    c_actions_count    integer DEFAULT 0 CHECK (c_actions_count >= 0),
    c_inventory        jsonb DEFAULT '[]',   -- array of collected item_ids
    c_npc_states       jsonb DEFAULT '{}',   -- per-NPC relationship flags
    c_scene_progress   jsonb DEFAULT '{}',   -- objectives completed per scene
    c_npc_voices       jsonb DEFAULT '{}',   -- cached TTS voice assignments
    c_current_lesson_id integer,
    c_current_module_context jsonb,          -- {module_name, grammar_focus, cefr_level}
    c_is_completed     boolean DEFAULT false,
    c_completed_at     timestamp,
    c_started_at       timestamp DEFAULT CURRENT_TIMESTAMP,
    c_last_interaction_at timestamp DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (c_user_id, c_story_id)
);

CREATE INDEX idx_story_progress_user   ON public.t_story_user_progress (c_user_id);
CREATE INDEX idx_story_progress_active ON public.t_story_user_progress (c_user_id, c_is_completed);

-- =============================================================================
-- Story: user interactions (dialogue history)
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.t_story_user_interactions (
    c_interaction_id  integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    c_user_id         bigint NOT NULL REFERENCES public.t_user(c_user_id) ON DELETE CASCADE,
    c_story_id        integer NOT NULL REFERENCES public.t_story_interactive_stories(c_story_id) ON DELETE CASCADE,
    c_scene_id        integer NOT NULL REFERENCES public.t_story_scenes(c_scene_id) ON DELETE CASCADE,
    c_interaction_type varchar(20) NOT NULL
                       CHECK (c_interaction_type IN ('dialogue','action','item_use','look_around')),
    c_user_input      text NOT NULL,
    c_user_input_type varchar(10) CHECK (c_user_input_type IN ('text','voice','action')),
    c_target_npc_id   integer REFERENCES public.t_story_npcs(c_npc_id) ON DELETE SET NULL,
    c_target_item_id  integer REFERENCES public.t_story_items(c_item_id) ON DELETE SET NULL,
    c_ai_response     text,           -- NPC reply text
    c_ai_response_trs jsonb,          -- translations {ru: "..."}
    c_correction      text,           -- grammar correction for user input
    c_correction_trs  jsonb,
    c_audio_filename  varchar(200),   -- TTS audio file for NPC reply
    c_timestamp       timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_story_interaction_user      ON public.t_story_user_interactions (c_user_id);
CREATE INDEX idx_story_interaction_story     ON public.t_story_user_interactions (c_story_id);
CREATE INDEX idx_story_interaction_timestamp ON public.t_story_user_interactions (c_user_id, c_timestamp DESC);

-- =============================================================================
-- Story: narrator hints shown to user
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.t_story_narrator_hints (
    c_hint_id   integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    c_user_id   bigint  NOT NULL REFERENCES public.t_user(c_user_id) ON DELETE CASCADE,
    c_story_id  integer NOT NULL REFERENCES public.t_story_interactive_stories(c_story_id) ON DELETE CASCADE,
    c_scene_id  integer NOT NULL REFERENCES public.t_story_scenes(c_scene_id) ON DELETE CASCADE,
    c_hint_type varchar(20) DEFAULT 'inner_thought'
                CHECK (c_hint_type IN ('inner_thought','observation','suggestion')),
    c_hint_text text NOT NULL,
    c_hint_text_trs jsonb,
    c_shown_at  timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_story_hint_user  ON public.t_story_narrator_hints (c_user_id);
CREATE INDEX idx_story_hint_scene ON public.t_story_narrator_hints (c_scene_id);

-- =============================================================================
-- Story: user-story library (ratings, favorites)
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.t_story_user_stories (
    c_id           integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    c_user_id      bigint  NOT NULL REFERENCES public.t_user(c_user_id) ON DELETE CASCADE,
    c_story_id     integer NOT NULL REFERENCES public.t_story_interactive_stories(c_story_id) ON DELETE CASCADE,
    c_started_at   timestamp DEFAULT CURRENT_TIMESTAMP,
    c_last_played_at timestamp DEFAULT CURRENT_TIMESTAMP,
    c_completed_at timestamp,
    c_is_completed boolean DEFAULT false,
    c_is_favorite  boolean DEFAULT false,
    c_user_rating  integer CHECK (c_user_rating BETWEEN 1 AND 5),
    c_user_review  text,
    UNIQUE (c_user_id, c_story_id)
);

CREATE INDEX idx_user_stories_user_id     ON public.t_story_user_stories (c_user_id);
CREATE INDEX idx_user_stories_last_played ON public.t_story_user_stories (c_user_id, c_last_played_at DESC);

-- =============================================================================
-- Story: NPC revealed facts tracking
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.t_story_user_revealed_facts (
    c_id          integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    c_progress_id integer NOT NULL REFERENCES public.t_story_user_progress(c_progress_id) ON DELETE CASCADE,
    c_user_id     integer NOT NULL REFERENCES public.t_user(c_user_id) ON DELETE CASCADE,
    c_story_id    integer NOT NULL REFERENCES public.t_story_interactive_stories(c_story_id) ON DELETE CASCADE,
    c_scene_id    integer NOT NULL REFERENCES public.t_story_scenes(c_scene_id) ON DELETE CASCADE,
    c_npc_id      integer NOT NULL REFERENCES public.t_story_npcs(c_npc_id) ON DELETE CASCADE,
    c_fact_index  integer NOT NULL,  -- index in NPC information_pool.facts array (0-based)
    c_revealed_at timestamp DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (c_progress_id, c_scene_id, c_npc_id, c_fact_index)
);

-- =============================================================================
-- Triggers: auto-update timestamps and ratings
-- =============================================================================

CREATE OR REPLACE FUNCTION public.update_story_timestamp()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN NEW.c_updated_at = CURRENT_TIMESTAMP; RETURN NEW; END;
$$;

CREATE TRIGGER trigger_story_updated_at
    BEFORE UPDATE ON public.t_story_interactive_stories
    FOR EACH ROW EXECUTE FUNCTION public.update_story_timestamp();

CREATE OR REPLACE FUNCTION public.update_story_rating(p_story_id integer)
RETURNS void LANGUAGE plpgsql AS $$
BEGIN
    UPDATE public.t_story_interactive_stories
    SET c_rating_avg = (
        SELECT ROUND(AVG(c_user_rating)::numeric, 2)
        FROM public.t_story_user_stories
        WHERE c_story_id = p_story_id AND c_user_rating IS NOT NULL
    )
    WHERE c_story_id = p_story_id;
END;
$$;

CREATE OR REPLACE FUNCTION public.trigger_update_story_rating()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN PERFORM public.update_story_rating(NEW.c_story_id); RETURN NEW; END;
$$;

CREATE TRIGGER trg_update_rating
    AFTER INSERT OR UPDATE OF c_user_rating ON public.t_story_user_stories
    FOR EACH ROW WHEN (NEW.c_user_rating IS NOT NULL)
    EXECUTE FUNCTION public.trigger_update_story_rating();

-- =============================================================================
-- Utility functions
-- =============================================================================

CREATE OR REPLACE FUNCTION public.get_user_stories(p_user_id bigint)
RETURNS TABLE (
    story_id integer, story_name varchar, description text,
    genre varchar, difficulty_level integer, is_completed boolean,
    started_at timestamp, last_played_at timestamp,
    user_rating integer, is_favorite boolean
) LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT s.c_story_id, s.c_story_name, s.c_description, s.c_genre,
           s.c_difficulty_level, us.c_is_completed, us.c_started_at,
           us.c_last_played_at, us.c_user_rating, us.c_is_favorite
    FROM public.t_story_interactive_stories s
    INNER JOIN public.t_story_user_stories us ON s.c_story_id = us.c_story_id
    WHERE us.c_user_id = p_user_id
    ORDER BY us.c_last_played_at DESC;
END;
$$;

CREATE OR REPLACE FUNCTION public.get_public_stories(
    p_difficulty_level integer DEFAULT NULL,
    p_genre varchar DEFAULT NULL
) RETURNS TABLE (
    story_id integer, story_name varchar, description text,
    genre varchar, difficulty_level integer, rating_avg numeric,
    times_completed integer, times_started integer, estimated_minutes integer
) LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT s.c_story_id, s.c_story_name, s.c_description, s.c_genre,
           s.c_difficulty_level, s.c_rating_avg, s.c_times_completed,
           s.c_times_started, s.c_estimated_minutes
    FROM public.t_story_interactive_stories s
    WHERE s.c_is_public = TRUE AND s.c_is_active = TRUE
      AND (p_difficulty_level IS NULL OR s.c_difficulty_level = p_difficulty_level)
      AND (p_genre IS NULL OR s.c_genre = p_genre)
    ORDER BY s.c_rating_avg DESC, s.c_times_completed DESC;
END;
$$;

-- =============================================================================
-- Log database (separate DB: engDBLog)
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.t_log_type (
    c_id   integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    c_desc text
);

CREATE TABLE IF NOT EXISTS public.t_log (
    c_log_id      bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    c_log_user_id bigint,
    c_log_txt     text,
    c_log_date    timestamp,
    c_log_type    integer REFERENCES public.t_log_type(c_id) ON UPDATE CASCADE ON DELETE CASCADE,
    c_log2        text,
    c_log3        text,
    c_log4        text
);
