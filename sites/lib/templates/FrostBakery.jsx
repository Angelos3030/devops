import s from './FrostBakery.module.css'
import Brand from './Brand'
import FindUs from './FindUs'
import SocialLinks from './SocialLinks'

export default function FrostBakery({ data: d }) {
  return (
    <div className={s.root}>
      <input type="checkbox" id="nav-toggle" className={s.navToggle} />
      <label htmlFor="nav-toggle" className={s.hamburger} aria-label="Toggle navigation menu">
        <div className={s.hamburgerLines}>
          <span></span>
          <span></span>
          <span></span>
        </div>
      </label>

      <aside className={s.sidebar} id="sidebar" role="navigation" aria-label="Main navigation">
        <div className={s.sidebarBrand}>
          <Brand data={d} />
          {d.TAGLINE && <div className={s.sidebarTagline}>{d.TAGLINE}</div>}
        </div>

        <nav className={s.sidebarNav}>
          <ul>
            <li><a href="#hero" className={s.active}><span className={s.navIcon}>◈</span> Home</a></li>
            {d.services?.length > 0 && (
              <>
                <li><a href="#flavors"><span className={s.navIcon}>✿</span> Flavors</a></li>
                <li><a href="#builder"><span className={s.navIcon}>★</span> Build Yours</a></li>
              </>
            )}
            <li><a href="#contact"><span className={s.navIcon}>✉</span> Contact</a></li>
          </ul>
        </nav>

        {d.HOURS?.length > 0 && (
          <div className={s.sidebarFooter}>
            <div className={s.sidebarHours}>
              <strong>Ωράριο</strong><br />
              {d.HOURS}
            </div>
          </div>
        )}
      </aside>

      <main className={s.main}>
        <section className={s.hero} id="hero">
          <div className={s.heroContent}>
            <h1 className={s.heroTitle}>{d.NAME}</h1>
            {d.TAGLINE && <p className={s.heroSubtitle}>{d.TAGLINE}</p>}
            {d.story?.[0]?.p && <p className={s.heroText}>{d.story[0].p}</p>}
            <div className={s.heroActions}>
              {d.services?.length > 0 && (
                <a href="#flavors" className={`${s.btn} ${s.btnPrimary}`}>Explore Flavors</a>
              )}
              <a href="#contact" className={`${s.btn} ${s.btnOutline}`}>Contact Us</a>
            </div>
          </div>

          <div className={s.heroDeco} aria-hidden="true">
            <div className={`${s.scoop} ${s.scoopStrawberry}`}><div className={s.scoopHighlight}></div></div>
            <div className={`${s.scoop} ${s.scoopMint}`}><div className={s.scoopHighlight}></div></div>
            <div className={`${s.scoop} ${s.scoopVanilla}`}><div className={s.scoopHighlight}></div></div>
          </div>
        </section>

        {d.services?.length > 0 && (
          <section className={`${s.section} ${s.sectionAlt} ${s.flavorsSection}`} id="flavors">
            <div className={s.sectionHeader}>
              <span className={s.sectionLabel}>Flavor Wheel</span>
              <h2 className={s.sectionTitle}>Pick your perfect scoop</h2>
              <p className={s.sectionDesc}>From timeless classics to rotating experiments, every flavor starts with a small-batch recipe and whole, real ingredients.</p>
            </div>

            <div className={s.marquee}>
              <div className={s.marqueeTrack}>
                {d.services.map((svc, i) => (
                  <div className={s.flavorCard} key={`a-${i}`}>
                    <div className={s.flavorCardSwatch}></div>
                    <div className={s.flavorCardInfo}>
                      <span className={s.flavorCardType}>Service</span>
                      <h3 className={s.flavorCardName}>{svc.title}</h3>
                      <p className={s.flavorCardDesc}>{svc.desc}</p>
                    </div>
                  </div>
                ))}
                {d.services.map((svc, i) => (
                  <div className={s.flavorCard} key={`b-${i}`} aria-hidden="true">
                    <div className={s.flavorCardSwatch}></div>
                    <div className={s.flavorCardInfo}>
                      <span className={s.flavorCardType}>Service</span>
                      <h3 className={s.flavorCardName}>{svc.title}</h3>
                      <p className={s.flavorCardDesc}>{svc.desc}</p>
                    </div>
                  </div>
                ))}
              </div>

              <div className={`${s.marqueeTrack} ${s.marqueeTrackReverse}`}>
                {d.services.map((svc, i) => (
                  <div className={s.flavorCard} key={`c-${i}`}>
                    <div className={s.flavorCardSwatch}></div>
                    <div className={s.flavorCardInfo}>
                      <span className={s.flavorCardType}>Service</span>
                      <h3 className={s.flavorCardName}>{svc.title}</h3>
                      <p className={s.flavorCardDesc}>{svc.desc}</p>
                    </div>
                  </div>
                ))}
                {d.services.map((svc, i) => (
                  <div className={s.flavorCard} key={`d-${i}`} aria-hidden="true">
                    <div className={s.flavorCardSwatch}></div>
                    <div className={s.flavorCardInfo}>
                      <span className={s.flavorCardType}>Service</span>
                      <h3 className={s.flavorCardName}>{svc.title}</h3>
                      <p className={s.flavorCardDesc}>{svc.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}

        {d.services?.length > 0 && (
          <section className={`${s.section} ${s.builder}`} id="builder">
            <div className={s.sectionHeader}>
              <span className={s.sectionLabel}>Build Your Own</span>
              <h2 className={s.sectionTitle}>Your sundae, your rules</h2>
              <p className={s.sectionDesc}>Walk through our four-step sundae builder at the counter or order ahead for pickup. Over 2,000 combinations to try.</p>
            </div>

            <div className={s.builderLayout}>
              <div className={s.builderSteps}>
                {d.services.map((svc, i) => (
                  <div className={s.builderStep} key={i}>
                    <div className={s.builderStepNum}>{i + 1}</div>
                    <div>
                      <h3 className={s.builderStepTitle}>{svc.title}</h3>
                      <p className={s.builderStepText}>{svc.desc}</p>
                    </div>
                  </div>
                ))}
              </div>

              <div className={s.builderPreview}>
                <div className={s.builderPreviewBowl}>
                  <div className={`${s.builderPreviewScoop} ${s.builderPreviewScoop1}`}></div>
                  <div className={`${s.builderPreviewScoop} ${s.builderPreviewScoop2}`}></div>
                  <div className={`${s.builderPreviewScoop} ${s.builderPreviewScoop3}`}></div>
                </div>
                {d.services[0]?.price && (
                  <p className={s.builderPreviewPrice}>From {d.services[0].price}</p>
                )}
              </div>
            </div>
          </section>
        )}

        <section className={s.section} id="contact">
          <FindUs data={d} />
        </section>

        <footer className={s.footer}>
          <div className={s.footerTop}>
            <SocialLinks data={d} />
          </div>
          <div className={s.footerBottom}>
            <p>&copy; {new Date().getFullYear()} {d.NAME}. All rights reserved.</p>
          </div>
        </footer>
      </main>
    </div>
  )
}
