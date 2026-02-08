import "./index.css";

const expeditions = [
  {
    title: "Glacial Highlands",
    date: "October 2023",
    description: "Wind-cut ridgelines and slate-blue valleys above the tree line.",
    image:
      "https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=1400&q=80",
  },
  {
    title: "Desert Passage",
    date: "August 2023",
    description: "Long asphalt ribbons leading into rust and sandstone labyrinths.",
    image:
      "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1400&q=80",
  },
  {
    title: "City at Dawn",
    date: "May 2023",
    description: "Neon traces softening into morning fog across concrete canyons.",
    image:
      "https://images.unsplash.com/photo-1489515217757-5fd1be406fef?auto=format&fit=crop&w=1400&q=80",
  },
];

const categories = [
  {
    title: "Landscapes",
    image:
      "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1400&q=80",
    size: "large",
  },
  {
    title: "Architecture",
    image:
      "https://images.unsplash.com/photo-1489515217757-5fd1be406fef?auto=format&fit=crop&w=1200&q=80",
    size: "small",
  },
  {
    title: "Nature",
    image:
      "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?auto=format&fit=crop&w=1200&q=80",
    size: "small",
  },
  {
    title: "Travel Series",
    image:
      "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=1400&q=80",
    size: "wide",
  },
];

const stories = [
  {
    title: "Echoes of the Mountain",
    date: "08.02.2026",
    description: "Why we climb when the world tells us to stay low.",
    image:
      "https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=1400&q=80",
  },
  {
    title: "Lost in the Fog",
    date: "14.01.2026",
    description: "A morning walk that turned into a journey inward.",
    image:
      "https://images.unsplash.com/photo-1482192596544-9eb780fc7f66?auto=format&fit=crop&w=1400&q=80",
  },
];

export default function App() {
  return (
    <div className="page">
      <header className="site-header">
        <div className="brand">Romanweiß</div>
        <nav className="nav">
          <a href="#journey">Journey</a>
          <a href="#expeditions">Expeditions</a>
          <a href="#stories">Stories</a>
          <a href="#contact">Contact</a>
        </nav>
      </header>

      <section id="journey" className="hero">
        <div className="hero-media" />
        <div className="hero-overlay" />
        <div className="hero-content">
          <p className="hero-kicker">Travel & Expedition Photography</p>
          <h1>Romanweiß</h1>
          <p className="hero-subtitle">
            Exploring landscapes, architecture, and the distance between moments.
          </p>
          <div className="hero-scroll">Scroll to begin</div>
        </div>
      </section>

      <section className="journal-intro">
        <p>
          “We travel not to escape life, but for life not to escape us. This
          journal is a collection of moments from the road — a visual diary of
          silence, texture, and light.”
        </p>
      </section>

      <section id="expeditions" className="section expeditions">
        <div className="section-heading">
          <div>
            <p className="section-eyebrow">The Journal</p>
            <h2>Recent Expeditions</h2>
            <p className="section-subtitle">Journeys into the remote.</p>
          </div>
          <button className="ghost-button" type="button">
            View all →
          </button>
        </div>
        <div className="expedition-grid">
          {expeditions.map((expedition) => (
            <article key={expedition.title} className="expedition-card">
              <div
                className="expedition-image"
                style={{ backgroundImage: `url(${expedition.image})` }}
              >
                <span>{expedition.date}</span>
              </div>
              <div className="expedition-copy">
                <h3>{expedition.title}</h3>
                <p>{expedition.description}</p>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="section categories">
        <div className="section-heading">
          <div>
            <p className="section-eyebrow">Portfolio</p>
            <h2>Fields of Focus</h2>
            <p className="section-subtitle">
              Visual separation through imagery, not boxes.
            </p>
          </div>
        </div>
        <div className="category-grid">
          {categories.map((category) => (
            <div
              key={category.title}
              className={`category-card ${category.size}`}
              style={{ backgroundImage: `url(${category.image})` }}
            >
              <div className="category-overlay">
                <h3>{category.title}</h3>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section id="stories" className="section stories">
        <div className="section-heading center">
          <p className="section-eyebrow">Visual Stories</p>
          <h2>Selected Stories</h2>
        </div>
        <div className="story-list">
          {stories.map((story, index) => (
            <article
              key={story.title}
              className={`story-item ${index % 2 === 0 ? "" : "reverse"}`}
            >
              <div
                className="story-image"
                style={{ backgroundImage: `url(${story.image})` }}
              />
              <div className="story-copy">
                <span>{story.date}</span>
                <h3>{story.title}</h3>
                <p>{story.description}</p>
                <button className="link-button" type="button">
                  Read full story
                </button>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section id="contact" className="section contact">
        <div className="contact-inner">
          <div className="contact-copy">
            <h2>Get in touch</h2>
            <p>
              Interested in a collaboration, a print, or just want to say hello?
              I’m always open to discussing new projects and creative
              opportunities.
            </p>
            <div className="contact-details">
              <div>
                <p className="detail-label">Location</p>
                <p>Berlin, Germany</p>
              </div>
              <div>
                <p className="detail-label">Email</p>
                <p>hello@romanweiss.com</p>
              </div>
              <div>
                <p className="detail-label">Socials</p>
                <p>Instagram · Behance · Vimeo</p>
              </div>
            </div>
          </div>
          <form className="contact-form">
            <label>
              Name
              <input type="text" placeholder="Your name" />
            </label>
            <label>
              Email
              <input type="email" placeholder="your@email.com" />
            </label>
            <label>
              Message
              <textarea placeholder="Tell me about your project..." rows={4} />
            </label>
            <button type="submit">Send message</button>
          </form>
        </div>
      </section>

      <footer className="footer">
        <div>
          <h3>Romanweiß</h3>
          <p>
            Capturing the silence of remote places, the texture of the wind, and
            the stories found in distance.
          </p>
        </div>
        <div className="footer-links">
          <div>
            <p className="detail-label">Explore</p>
            <p>Expeditions</p>
            <p>Journal</p>
            <p>Prints</p>
            <p>Collaborate</p>
          </div>
          <div>
            <p className="detail-label">Social</p>
            <div className="socials">
              <span>IG</span>
              <span>X</span>
              <span>Mail</span>
            </div>
          </div>
          <div>
            <p className="detail-label">Newsletter</p>
            <p>Updates from the road, once a month.</p>
            <div className="newsletter">
              <input type="email" placeholder="Email address" />
              <button type="button">Join</button>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}