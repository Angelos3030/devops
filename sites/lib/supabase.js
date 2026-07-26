'use client'
import { createClient } from '@supabase/supabase-js'

// Ο browser client για το dashboard login (Google + magic link).
// Χρησιμοποιεί το ΔΗΜΟΣΙΟ anon key — ασφαλές για client-side (RLS + το δικό μας API auth).
const url = process.env.NEXT_PUBLIC_SUPABASE_URL || ''
const anon = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''

export const supabaseReady = Boolean(url && anon)

export const supabase = supabaseReady
  ? createClient(url, anon, { auth: { persistSession: true, autoRefreshToken: true } })
  : null
