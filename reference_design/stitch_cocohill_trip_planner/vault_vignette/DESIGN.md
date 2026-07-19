---
name: Vault & Vignette
colors:
  surface: '#fff8f5'
  surface-dim: '#f6d4b6'
  surface-bright: '#fff8f5'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#fff1e7'
  surface-container: '#ffeada'
  surface-container-high: '#ffe3cc'
  surface-container-highest: '#fedcbe'
  on-surface: '#291806'
  on-surface-variant: '#4d4635'
  inverse-surface: '#402c18'
  inverse-on-surface: '#ffeee0'
  outline: '#7f7663'
  outline-variant: '#d0c5af'
  surface-tint: '#735c00'
  primary: '#735c00'
  on-primary: '#ffffff'
  primary-container: '#d4af37'
  on-primary-container: '#554300'
  inverse-primary: '#e9c349'
  secondary: '#006e20'
  on-secondary: '#ffffff'
  secondary-container: '#90f691'
  on-secondary-container: '#007322'
  tertiary: '#5e604d'
  on-tertiary: '#ffffff'
  tertiary-container: '#b4b49d'
  on-tertiary-container: '#454634'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffe088'
  primary-fixed-dim: '#e9c349'
  on-primary-fixed: '#241a00'
  on-primary-fixed-variant: '#574500'
  secondary-fixed: '#93f993'
  secondary-fixed-dim: '#77dc7a'
  on-secondary-fixed: '#002105'
  on-secondary-fixed-variant: '#005316'
  tertiary-fixed: '#e4e4cc'
  tertiary-fixed-dim: '#c8c8b0'
  on-tertiary-fixed: '#1b1d0e'
  on-tertiary-fixed-variant: '#474836'
  background: '#fff8f5'
  on-background: '#291806'
  surface-variant: '#fedcbe'
  parchment-white: '#FDFBF7'
  mint-green: '#98FF98'
  coin-gold: '#D4AF37'
  ink-black: '#1A1A1A'
  inheritance-red: '#C41E3A'
typography:
  headline-lg:
    fontFamily: Bricolage Grotesque
    fontSize: 48px
    fontWeight: '800'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Bricolage Grotesque
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
  headline-sm:
    fontFamily: Bricolage Grotesque
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
  body-lg:
    fontFamily: Literata
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Literata
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.05em
  headline-lg-mobile:
    fontFamily: Bricolage Grotesque
    fontSize: 36px
    fontWeight: '800'
    lineHeight: 44px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 8px
  gutter: 24px
  margin: 32px
  container-max: 1120px
---

## Brand & Style

The design system is an exercise in "Luxury Nostalgia." It draws inspiration from the Golden Age of comics and mid-century wealth aesthetics, specifically channeling the whimsical opulence of the 1950s and 60s. The brand personality is "Affably Affluent"—a mix of high-society prestige and playful, hand-drawn warmth. 

The design style is **Illustrated Neo-Vintage**. It combines heavy, ink-like strokes with a refined pastel palette. Key visual motifs include thick, slightly irregular borders that mimic hand-drawn ink, Ben-Day dot patterns for subtle depth, and character-driven cues like money bags, monocles, and top hats. The goal is to make the often-stressful task of bank statement analysis feel like a charming Sunday morning comic strip.

## Colors

The palette is anchored in a "Creamy Beige" (Parchment White) background to evoke vintage paper stock. 

- **Primary:** Coin Gold is used for primary actions, success states, and key highlights, representing wealth and value.
- **Secondary:** Mint Green serves as the secondary accent, nodding to classic paper currency.
- **Neutral:** Instead of pure grays, we use "Ink Black" and deep "Chocolate Brown" for borders and text to maintain the hand-drawn comic aesthetic.
- **Tertiary:** Used for large surface areas and containers to differentiate sections without losing the warmth of the parchment.

## Typography

The typography strategy balances whimsy with legibility. 

- **Headlines:** We use **Bricolage Grotesque** for its quirky, expressive character. It mimics the bold, hand-lettered titles of vintage comic books.
- **Body:** **Literata** provides a "bookish" and scholarly feel, ensuring that financial data remains highly readable while maintaining a classic editorial vibe.
- **Data & Labels:** **JetBrains Mono** is used for currency values and technical labels. This monospaced font provides a subtle nod to old-fashioned ledger entries and typewriter-style bank receipts.

## Layout & Spacing

The layout follows a **Fixed Grid** approach on desktop to mimic the structured panels of a comic strip. Content is contained within "Panels" that have generous internal padding to ensure the "Richie Rich" luxury feel isn't lost to clutter.

- **Desktop:** 12-column grid with wide 24px gutters. Sections are clearly delineated by thick 3px ink borders.
- **Tablet:** 8-column grid with 20px gutters. 
- **Mobile:** 4-column grid. Borders may be thinned to 2px to maximize screen real estate, and characters are moved to the background or top-right corners of cards.

Use an 8px spacing rhythm for all margins and paddings to ensure a balanced, professional feel within the whimsical exterior.

## Elevation & Depth

This design system eschews modern blurred shadows in favor of **Graphic Depth**. 

1. **Hard Drop Shadows:** Instead of blurs, use solid color offsets (usually in a slightly darker tan or gold) to push elements forward. This mimics the "pop" of 2D comic art.
2. **Ink Borders:** Hierarchy is primarily established through border weight. Primary containers use 3px borders, while secondary elements use 1.5px.
3. **Halftone Textures:** Use subtle Ben-Day dot patterns in the background of active cards or headers to create a sense of tactile, printed material.
4. **Stacked Panels:** Layering is achieved by physical overlaps (e.g., a "Money Bag" character illustration peeking over the edge of a card) rather than Z-axis blurs.

## Shapes

The shape language is "Bubbly but Structured." We use **Rounded** corners (level 2) to maintain a friendly, approachable comic feel, avoiding the harshness of sharp corners. 

Elements like buttons and input fields should feel substantial and "squishy." Illustrations should always have soft, curved edges, even when representing hard objects like vaults or coins.

## Components

- **Buttons:** Use a "3D Block" style. A primary button is Gold with a thick Black border and a solid Black offset shadow. On hover, the button should "press" down by reducing the shadow offset.
- **Input Fields:** Styled like traditional ledger entries. A thick bottom border and a faint cream fill. Focus states should highlight the border in Mint Green.
- **Cards (Panels):** Each card should look like a comic panel. Include a small "character cameo" in the corner of summary cards (e.g., a character with a monocle looking at your "Investment" card).
- **Chips:** Styled like vintage postage stamps or gold coins, with scalloped edges or circular forms and thick outlines.
- **Checkboxes:** Designed as small "X" marks in an ink-drawn box, avoiding the sterile checkmark of modern OS styles.
- **The "Vault" Progress Bar:** Use a golden bar that fills a vault-shaped container.
- **Character Illustrations:** Integrate spot illustrations of 50s-style wealthy characters to provide feedback (e.g., a character holding an empty wallet for a "low balance" alert).