# 18 - Vertical Design Intelligence

> Vitrina does not recolor one generic website. It combines a profession preset,
> a compatible design system, and the customer's own brand/content.

## The generation order

1. Detect the business vertical from the intake.
2. Load that vertical's conversion goal, required sections, media rules and no-go rules.
3. Rank only design systems that suit that business.
4. Apply the customer's brand, photos, copy, location and offer.
5. Generate nine genuinely different previews when enough content exists.
6. Validate mobile, accessibility, SEO and the primary conversion before publishing.

Changing only colors or fonts does not count as a different preview. Each preview must
change the layout, hero composition, content rhythm, typography, motion language and
section treatment.

## Vertical families

| Vertical | Primary conversion | Required content | Visual direction | Avoid |
|---|---|---|---|---|
| Restaurant / taverna | Reservation, call, directions | Menu, signature dishes, hours, map | Appetite, atmosphere, warm human photography | Corporate service grids |
| Cafe / bakery | Visit, directions, order | Products, atmosphere, hours, map | Daylight, texture, editorial product moments | Dark luxury by default |
| Dentist / medical | Book appointment, call | Services, practitioner, credentials, hours, map | Calm, clean, reassuring, highly legible | Aggressive motion, alarming claims, unconsented before/after |
| Gym / fitness | Trial session, membership lead | Programs, coaches, schedule, facilities | Energy, movement, progress, bold type | Passive luxury, dense medical copy |
| Beauty / salon | Book appointment | Services, price cues, work gallery, hours | Fashion/editorial, transformation, personal style | Industrial trade styling |
| Carpenter / maker | Quote request, project enquiry | Portfolio, materials, process, service area | Project-first, tactile craft, detail photography | Generic stock construction imagery |
| Home trade / technician | Immediate call, quote | Services, areas served, availability, proof | Fast, direct, dependable, mobile-first | Decorative intros that hide the phone |
| Lawyer / accountant / consultant | Consultation lead | Expertise, team, process, contact | Authority, discretion, clarity | Playful novelty that weakens trust |
| Hospitality / rooms | Direct booking | Rooms, amenities, location, availability path | Immersive place and experience | Service-card-heavy SaaS layouts |
| Garage / automotive | Service booking, call | Services, brands, process, hours, location | Technical confidence, precision, speed | Lifestyle imagery unrelated to the workshop |
| Retail / local shop | Visit, product enquiry, purchase | Categories, products, hours, map | Product-first merchandising | Long agency-style manifestos |
| Farm / producer | Order, visit, wholesale lead | Products, provenance, process, certifications | Land, origin, packaging, human story | Fake rustic decoration and unsupported claims |

## Example: dentist vs gym

### Dentist

- Hero: practitioner/space, short reassurance, `Book appointment`.
- Sections: treatments, practitioner, trust/credentials, approach, hours, map, FAQ.
- Motion: subtle fades, restrained image reveals, no constant marquees.
- Palette: not automatically blue; use calm mineral, warm white, sage or precise monochrome.
- SEO: `Dentist` schema, treatment + area pages, real practitioner and address data.

### Gym

- Hero: real training in motion, trial CTA, schedule shortcut.
- Sections: programs, coaches, facilities, timetable, membership path, location.
- Motion: kinetic typography, counters and scroll-linked imagery with a reduced-motion fallback.
- Palette: high energy without forcing neon green; contrast must remain accessible.
- SEO: `ExerciseGym` schema, programs, hours, area and trial-session intent.

## Nine design systems

The nine systems are universal structures, not profession skins:

1. Material Atelier - tactile editorial craft.
2. Sculptural Noir - cinematic gallery.
3. Workshop Modernism - technical Swiss system.
4. Cinematic Residence - immersive spatial storytelling.
5. Type Gallery - expressive graphic editorial.
6. Quiet Precision - calm minimal craft and care.
7. Kinetic Workshop - motion-led typography and clipped reveals.
8. Infinite Showroom - horizontal/parallax project journey.
9. Living Material - organic geometry and interactive material storytelling.

Not every system suits every vertical. The recommendation engine must rank compatibility
and may exclude a system when it harms trust, usability or conversion.

## Media policy

- Customer photos are always preferred and never silently replaced.
- With weak photos, improve cropping, sequencing and presentation before generating assets.
- With no photos, use licensed or generated profession-specific imagery and label provenance.
- Medical, legal and other trust-sensitive verticals must not imply a person, credential,
  result or facility that the customer did not provide.
- Every content image needs useful Greek alt text. Decorative images use empty alt text.

## Definition of done

- The page looks intentionally designed for that profession.
- The primary action is visible in the first viewport and remains easy on mobile.
- Required vertical sections exist; irrelevant sections do not.
- All nine previews are structurally distinct, not palette variants.
- Motion supports meaning and honors `prefers-reduced-motion`.
- Real business facts, consent, accessibility, local SEO and schema are verified.

