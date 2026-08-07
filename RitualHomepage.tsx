// RitualHomepage.tsx — the innovative replacement for the encyclopedia homepage.
//
// THE CONCEPT:
// Instead of showing 35 chapters, show ONE thing at a time.
// The homepage becomes a ritual, not an encyclopedia.
//
// STRUCTURE:
//   1. Opening line (a proverb) — just one line, with space
//   2. The daily card — one card, deeply
//   3. A whisper — a short story or teaching
//   4. Closing line
//
// Each visit is a ritual. You don't browse — you experience.

"use client";

import { useState, useEffect } from "react";
import { composeReading, type ReadingResult } from "@/engine";
import { PROVERBS, SOUL_STORIES, getTarotCard } from "@/content";
import { TarotCardImage } from "../TarotCardImage";

/** Pick a proverb based on the day (deterministic, changes daily). */
function pickDailyProverb(dayNumber: number) {
  if (!PROVERBS || PROVERBS.length === 0) return null;
  return PROVERBS[dayNumber % PROVERBS.length];
}

/** Pick a story based on the day (deterministic, changes daily). */
function pickDailyStory(dayNumber: number) {
  if (!SOUL_STORIES || SOUL_STORIES.length === 0) return null;
  return SOUL_STORIES[dayNumber % SOUL_STORIES.length];
}

export function RitualHomepage() {
  const [reading, setReading] = useState<ReadingResult | null>(null);
  const [dayNumber, setDayNumber] = useState(0);

  useEffect(() => {
    // Compute the daily reading
    const result = composeReading(new Date());
    setReading(result);
    // Day number for deterministic content selection
    const now = new Date();
    const start = new Date(now.getFullYear(), 0, 0);
    const diff = now.getTime() - start.getTime();
    setDayNumber(Math.floor(diff / (1000 * 60 * 60 * 24)));
  }, []);

  const proverb = pickDailyProverb(dayNumber);
  const story = pickDailyStory(dayNumber);
  const card = reading ? getTarotCard(reading.cardNumber) : null;

  return (
    <div className="ritual-homepage">
      {/* OPENING: one line, with space */}
      <section className="ritual-opening">
        {proverb && (
          <p className="ritual-proverb">{proverb.text}</p>
        )}
      </section>

      {/* THE READING: one card, deeply */}
      <section className="ritual-reading">
        {card && (
          <>
            <TarotCardImage card={card} />
            <h2 className="ritual-card-name">{card.hebrewName}</h2>
            <p className="ritual-card-meaning">{card.description}</p>
          </>
        )}
      </section>

      {/* THE WHISPER: one story */}
      <section className="ritual-whisper">
        {story && (
          <>
            <h3 className="ritual-story-title">{story.title}</h3>
            <p className="ritual-story-body">{story.body}</p>
          </>
        )}
      </section>

      {/* CLOSING: one line */}
      <section className="ritual-closing">
        <p className="ritual-closing-line">היום עבר. מחר יבוא.</p>
      </section>
    </div>
  );
}