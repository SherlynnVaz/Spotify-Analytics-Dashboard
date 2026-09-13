import { useEffect, useRef, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function StatifyLogo() {
  return (
    <div className="logo-circle" aria-label="Statify logo">
      <svg viewBox="0 0 32 32" aria-hidden="true">
        <path d="M6 24V18M12 24V13M18 24V16M24 24V8" />
        <path d="m5 12 6-4 6 3 8-6" />
        <path d="M22 5h3v3" />
      </svg>
    </div>
  );
}

function DistributionChart({ title, description, items, accent = "green" }) {
  const maxValue = Math.max(...items.map((item) => item.value), 1);

  return (
    <section className="chart-panel">
      <div className="chart-heading">
        <div>
          <h2>{title}</h2>
          <p>{description}</p>
        </div>
        <span>DISTRIBUTION</span>
      </div>

      <div className="bar-chart">
        {items.map((item) => (
          <div className="bar-row" key={item.label}>
            <span className="bar-label">{item.label}</span>
            <div className="bar-track">
              <div
                className={`bar-fill ${accent}`}
                style={{ width: `${(item.value / maxValue) * 100}%` }}
              />
            </div>
            <span className="bar-value">{item.value}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function ReleaseTimeline({ items }) {
  const [hoveredIndex, setHoveredIndex] = useState(null);
  const maxValue = Math.max(...items.map((item) => item.value), 1);
  const points = items
    .map((item, index) => `${(index / Math.max(items.length - 1, 1)) * 100},${92 - (item.value / maxValue) * 78}`)
    .join(" ");
  const area = `0,100 ${points} 100,100`;

  return (
    <section className="chart-panel timeline-panel">
      <div className="chart-heading">
        <div>
          <h2>Release timeline</h2>
          <p>Hover a dot to see the number of tracks released that year.</p>
        </div>
        <span>ERA FLOW</span>
      </div>
      <div className="release-timeline">
        <svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-label="Tracks by release year">
          <polygon className="release-area" points={area} />
          <polyline className="release-line" points={points} />
        </svg>
        {items.map((item, index) => (
          <div
            className="release-point"
            key={item.label}
            style={{
              left: `${(index / Math.max(items.length - 1, 1)) * 100}%`,
              top: `${92 - (item.value / maxValue) * 78}%`,
            }}
            onMouseEnter={() => setHoveredIndex(index)}
            onMouseLeave={() => setHoveredIndex(null)}
          />
        ))}
        {hoveredIndex !== null && (
          <div
            className="release-hover-tooltip"
            style={{
              left: `${Math.min(Math.max((hoveredIndex / Math.max(items.length - 1, 1)) * 100, 8), 82)}%`,
            }}
          >
            {`${items[hoveredIndex].label}: ${items[hoveredIndex].value} tracks`}
          </div>
        )}
        <div className="timeline-labels">
          {items.map((item) => <span key={item.label}>{item.label}</span>)}
        </div>
      </div>
    </section>
  );
}

function DurationBubbles({ items }) {
  const maxValue = Math.max(...items.map((item) => item.value), 1);

  return (
    <section className="chart-panel duration-panel">
      <div className="chart-heading">
        <div>
          <h2>Track length fingerprint</h2>
          <p>Each bubble is a duration bucket. Larger means more tracks.</p>
        </div>
        <span>RUNTIME</span>
      </div>
      <div className="duration-bubbles">
        {items.map((item, index) => (
          <div
            className={`duration-bubble bubble-${index}`}
            key={item.label}
            style={{ width: `${58 + (item.value / maxValue) * 46}px`, height: `${58 + (item.value / maxValue) * 46}px` }}
            title={`${item.label}: ${item.value} tracks`}
          >
            <strong>{item.value}</strong>
            <span>{item.label}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function ArtistPyramid({ artists, artistImages }) {
  const maxValue = artists[0]?.value || 1;

  return (
    <section className="chart-panel pyramid-panel">
      <div className="chart-heading">
        <div>
          <h2>Artist pyramid</h2>
          <p>Artists appearing most often across your ranked tracks.</p>
        </div>
        <span>TOP ARTISTS</span>
      </div>
      <div className="artist-pyramid">
        {artists.map((artist, index) => (
          <div
            className="pyramid-row"
            key={artist.name}
            style={{ width: `${Math.max((artist.value / maxValue) * 100, 42)}%` }}
          >
            <span>{index + 1}</span>
            {artistImages[artist.name] ? (
              <img src={artistImages[artist.name]} alt="" />
            ) : null}
            <strong>{artist.name}</strong>
            <small>{artist.value} tracks</small>
          </div>
        ))}
      </div>
    </section>
  );
}

function DonutChart({ title, description, items }) {
  const total = items.reduce((sum, item) => sum + item.value, 0) || 1;
  const firstPercent = (items[0]?.value / total) * 100 || 0;

  return (
    <section className="chart-panel donut-panel">
      <div className="chart-heading">
        <div>
          <h2>{title}</h2>
          <p>{description}</p>
        </div>
        <span>SHARE</span>
      </div>
      <div className="donut-layout">
        <div
          className="donut"
          style={{ background: `conic-gradient(#1ed760 ${firstPercent}%, #4c9f70 ${firstPercent}% 100%)` }}
        >
          <div><strong>{Math.round(firstPercent)}%</strong><span>{items[0]?.label || "Tracks"}</span></div>
        </div>
        <div className="legend-list">
          {items.map((item, index) => (
            <div key={item.label}>
              <i className={`legend-dot dot-${index}`} />
              <span>{item.label}</span>
              <strong>{item.value}</strong>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function AlbumGallery({ tracks }) {
  const albums = tracks
    .filter((track) => track.image_url)
    .filter((track, index, items) => (
      items.findIndex((item) => item.album === track.album) === index
    ))
    .slice(0, 6);

  return (
    <section className="chart-panel album-gallery-panel">
      <div className="chart-heading">
        <div>
          <h2>Album landscape</h2>
          <p>The artwork behind your current top tracks.</p>
        </div>
        <span>ALBUMS</span>
      </div>
      <div className="album-gallery">
        {albums.map((album) => (
          <div className="album-tile" key={album.album}>
            <img src={album.image_url} alt={album.album} />
            <strong>{album.album}</strong>
            <span>{album.artist}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function AnalyticsDashboard({ analytics, topTracks, topArtists }) {
  const summary = analytics?.summary || {};
  const albumTypes = analytics?.album_types || [];
  const explicitItems = [
    { label: "Explicit", value: Math.round((summary.explicit_percent / 100) * (summary.tracks || 1)) },
    { label: "Clean", value: Math.max((summary.tracks || 1) - Math.round((summary.explicit_percent / 100) * (summary.tracks || 1)), 0) },
  ];
  const artistImages = Object.fromEntries(
    topArtists.map((artist) => [artist.name, artist.image_url])
  );
  const featuredTrack = topTracks[0];
  const trackArtistNames = (featuredTrack?.artist || "")
  .split(",")
  .map((name) => name.trim().toLowerCase())
  .filter(Boolean);

const featuredArtist =
    topArtists.find(
      (artist) => artist.artist_id === featuredTrack?.artist_id
    ) ||
    topArtists.find(
      (artist) =>
        trackArtistNames.includes(
          (artist.name || "").trim().toLowerCase()
        )
    );

  const featuredArtistImage =
    featuredTrack?.artist_image_url ||
    featuredArtist?.image_url ||
    null;

  return (
    <section className="analytics-workspace">
      <div className="analytics-hero">
        <div className="analytics-hero-copy">
          <p className="eyebrow">YOUR CURRENT SIGNAL</p>
          <h2>{featuredTrack?.name || "Your listening profile"}</h2>
          <p>{featuredTrack ? `${featuredTrack.artist} · ${featuredTrack.album}` : "Connect Spotify to reveal your listening patterns."}</p>
        </div>
        <div className="analytics-hero-art">
          {featuredTrack?.image_url && <div className="hero-art-item album-art"><img src={featuredTrack.image_url} alt={featuredTrack.album} /></div>}
          {featuredArtistImage && <div className="hero-art-item artist-art"><img src={featuredArtistImage} alt={featuredTrack?.artist || featuredArtist?.name} /></div>}
        </div>
      </div>
      <div className="analytics-kpis">
        <div><span>TRACKS ANALYSED</span><strong>{summary.tracks || 0}</strong></div>
        <div><span>UNIQUE ALBUMS</span><strong>{summary.unique_albums || 0}</strong></div>
        <div><span>AVG TRACK LENGTH</span><strong>{summary.average_duration || 0}m</strong></div>
        <div><span>COLLABORATIONS</span><strong>{summary.collaboration_percent || 0}%</strong></div>
      </div>

      <div className="insights-intro">
        <div>
          <p className="eyebrow">YOUR LISTENING, EXPLAINED</p>
          <h2>See what shapes your taste</h2>
        </div>
        <p>Explore the eras, artists, albums, and song lengths that make your listening yours.</p>
      </div>

      <div className="analytics-grid">
        <ReleaseTimeline items={analytics?.release_years || []} />
        <DistributionChart title="Release decade" description="The eras that define your current rotation." items={analytics?.release_decades || []} accent="mint" />
        <DurationBubbles items={analytics?.durations || []} />
        <DonutChart title="Album format" description="Album, single, and compilation mix." items={albumTypes} />
        <DonutChart title="Explicit vs clean" description="Share of explicit tracks in this range." items={explicitItems} />
        <DistributionChart title="Most represented albums" description="Albums contributing the most tracks." items={analytics?.albums || []} accent="gold" />
        <AlbumGallery tracks={topTracks} />
        <ArtistPyramid artists={analytics?.artist_pyramid || []} artistImages={artistImages} />
      </div>
    </section>
  );
}

function ListeningCharts({ recentlyPlayed }) {
  const hourBuckets = Array.from({ length: 12 }, (_, index) => ({
    label: `${String(index * 2).padStart(2, "0")}h`,
    value: 0,
  }));
  const dayBuckets = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    .map((label) => ({ label, value: 0 }));

  recentlyPlayed.forEach((track) => {
    const playedAt = new Date(track.played_at);
    hourBuckets[Math.floor(playedAt.getHours() / 2)].value += 1;
    dayBuckets[playedAt.getDay()].value += 1;
  });

  const maxHour = Math.max(...hourBuckets.map((bucket) => bucket.value), 1);
  const maxDay = Math.max(...dayBuckets.map((bucket) => bucket.value), 1);

  const hourPoints = hourBuckets.map((bucket, index) => {
    const x = (index / (hourBuckets.length - 1)) * 100;
    const y = 94 - (bucket.value / maxHour) * 78;
    return `${x},${y}`;
  }).join(" ");
  const hourArea = `0,100 ${hourPoints} 100,100`;

  function renderBars(items, maxValue) {
    return items.map((item) => (
      <div className="activity-bar" key={item.label}>
        <div
          className="activity-bar-fill"
          style={{ height: `${(item.value / maxValue) * 100}%` }}
          title={`${item.value} plays`}
        />
        <span>{item.label}</span>
      </div>
    ));
  }

  const peakHour = hourBuckets.reduce((peak, bucket) => (
    bucket.value > peak.value ? bucket : peak
  ), hourBuckets[0]);
  const peakDay = dayBuckets.reduce((peak, bucket) => (
    bucket.value > peak.value ? bucket : peak
  ), dayBuckets[0]);

  return (
    <section className="activity-view">
      <div className="activity-summary">
        <div>
          <span>RECENT PLAYS</span>
          <strong>{recentlyPlayed.length}</strong>
        </div>
        <div>
          <span>BUSIEST LISTENING PERIOD</span>
          <strong>{peakHour.label} to {String((Number(peakHour.label.slice(0, -1)) + 2) % 24).padStart(2, "0")}h</strong>
        </div>
        <div>
          <span>MOST ACTIVE DAY</span>
          <strong>{peakDay.label}</strong>
        </div>
      </div>

      <div className="activity-chart-grid">
        <section className="chart-panel activity-chart-panel">
          <div className="chart-heading">
            <div>
              <h2>Listening timeline</h2>
              <p>Play frequency across the day, in two-hour blocks.</p>
            </div>
            <span>DAILY RHYTHM</span>
          </div>
          <div className="timeline-chart">
            <svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-label="Listening frequency by time of day">
              <polygon className="timeline-area" points={hourArea} />
              <polyline className="timeline-line" points={hourPoints} />
            </svg>
            <div className="timeline-labels">
              {hourBuckets.map((bucket) => <span key={bucket.label}>{bucket.label}</span>)}
            </div>
          </div>
        </section>

        <section className="chart-panel activity-chart-panel">
          <div className="chart-heading">
            <div>
              <h2>Weekly listening pattern</h2>
              <p>How many recent plays fall on each day.</p>
            </div>
            <span>DAY DISTRIBUTION</span>
          </div>
          <div className="activity-chart">{renderBars(dayBuckets, maxDay)}</div>
        </section>
      </div>
    </section>
  );
}

function App() {
  const [user, setUser] = useState(null);
  const [topTracks, setTopTracks] = useState([]);
  const [topArtists, setTopArtists] = useState([]);
  const [recentlyPlayed, setRecentlyPlayed] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [timeRange, setTimeRange] = useState("medium_term");
  const [activeView, setActiveView] = useState("overview");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState(false);
  const dashboardRequest = useRef(0);

  useEffect(() => {
    loadDashboard(timeRange);
  }, [timeRange]);

  useEffect(() => {
    if (!user) return;

    const interval = setInterval(() => {
      refreshRecentlyPlayed();
    }, 60000);

    return () => clearInterval(interval);
  }, [user]);

  async function refreshRecentlyPlayed() {
    try {
      const response = await fetch(
        `${API_URL}/recently-played`,
        {
          credentials: "include",
          cache: "no-store",
        }
      );

      const data = await response.json();

      if (data.recently_played) {
        setRecentlyPlayed(data.recently_played);
      }
    } catch (error) {
      console.error("Recently played refresh error:", error);
    }
  }

  async function loadDashboard(selectedRange) {
    const requestId = ++dashboardRequest.current;

    try {
      const [
        userResponse,
        tracksResponse,
        artistsResponse,
        recentResponse,
        analyticsResponse,
      ] = await Promise.all([
        fetch(`${API_URL}/me`, {
          credentials: "include",
        }),
        fetch(`${API_URL}/top-tracks?time_range=${selectedRange}`, {
          credentials: "include",
        }),
        fetch(`${API_URL}/top-artists?time_range=${selectedRange}`, {
          credentials: "include",
        }),
        fetch(`${API_URL}/recently-played`, {
          credentials: "include",
        }),
        fetch(`${API_URL}/analytics?time_range=${selectedRange}`, {
          credentials: "include",
        }),
      ]);

      const userData = await userResponse.json();
      const tracksData = await tracksResponse.json();
      const artistsData = await artistsResponse.json();
      const recentData = await recentResponse.json();
      const analyticsData = await analyticsResponse.json();

      if (requestId !== dashboardRequest.current) {
        return;
      }

      if (userData.authenticated) {
        setUser(userData.user);
      }

      if (tracksData.tracks) {
        setTopTracks(tracksData.tracks);
      }

      if (artistsData.artists) {
        setTopArtists(artistsData.artists);
      }

      if (recentData.recently_played) {
        setRecentlyPlayed(recentData.recently_played);
      }

      if (!analyticsData.error) {
        setAnalytics(analyticsData);
      }

    } catch (error) {
      console.error("Dashboard loading error:", error);
    } finally {
      setLoading(false);
    }
  }

  function selectTimeRange(range) {
    setTimeRange(range);
  }

  function connectSpotify() {
    setConnecting(true);
    window.location.href = `${API_URL}/login`;
  }

  if (loading) {
    return (
      <div className="loading-screen">
        <StatifyLogo />
        <p>Loading your Spotify data...</p>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="app">
        <header className="navbar">
          <div className="logo">
            <StatifyLogo />
            <span>STATIFY</span>
          </div>
        </header>

        <main className="hero">
          <div className="hero-content">
            <p className="eyebrow">YOUR MUSIC. YOUR DATA.</p>

            <h1>
              Understand your
              <span> Spotify </span>
              listening habits.
            </h1>

            <p className="hero-description">
              Connect your Spotify account and discover your top artists,
              favourite tracks, listening patterns and more.
            </p>

            <button
              type="button"
              className="spotify-button"
              onClick={connectSpotify}
              disabled={connecting}
            >
              {connecting ? "Connecting..." : "Connect Spotify"}
            </button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className={`dashboard${sidebarCollapsed ? " sidebar-collapsed" : ""}`}>

      {/* SIDEBAR */}

      <aside className="sidebar">

        <div className="sidebar-logo">
          <StatifyLogo />
          <span className="sidebar-wordmark">STATIFY</span>
        </div>

        <button
          className="sidebar-toggle"
          type="button"
          aria-label={sidebarCollapsed ? "Expand navigation" : "Collapse navigation"}
          onClick={() => setSidebarCollapsed((collapsed) => !collapsed)}
        >
          {sidebarCollapsed ? ">" : "<"}
        </button>

        <nav>
          <button
            title="Overview"
            className={activeView === "overview" ? "active" : ""}
            onClick={() => setActiveView("overview")}
          >
            <span className="nav-icon">♫</span><span className="nav-label">Overview</span>
          </button>
          <button
            title="Music Insights"
            className={activeView === "music-insights" ? "active" : ""}
            onClick={() => setActiveView("music-insights")}
          >
            <span className="nav-icon">♪</span><span className="nav-label">Music Insights</span>
          </button>
          <button
            title="Listening Activity"
            className={activeView === "listening-activity" ? "active" : ""}
            onClick={() => setActiveView("listening-activity")}
          >
            <span className="nav-icon">♬</span><span className="nav-label">Listening Activity</span>
          </button>
        </nav>

      </aside>


      {/* MAIN CONTENT */}

      <main className={`main-content ${activeView}`}>

        {/* HEADER */}

        <header className="dashboard-header">

          <div>
            <h1>
              Welcome back, {user.display_name}
            </h1>

            <p className="subtitle">
              Here's what your Spotify listening looks like.
            </p>
          </div>

          <div className="profile">

            {user.image_url ? (
              <img
                src={user.image_url}
                alt={user.display_name}
              />
            ) : (
              <div className="profile-placeholder">
                {user.display_name?.charAt(0)}
              </div>
            )}

            <span>{user.display_name}</span>

          </div>

        </header>


        {/* TIME RANGE */}

        <div className="time-range">

          <button
            className={timeRange === "short_term" ? "selected" : ""}
            onClick={() => selectTimeRange("short_term")}
          >
            4 Weeks
          </button>

          <button
            className={timeRange === "medium_term" ? "selected" : ""}
            onClick={() => selectTimeRange("medium_term")}
          >
            6 Months
          </button>

          <button
            className={timeRange === "long_term" ? "selected" : ""}
            onClick={() => selectTimeRange("long_term")}
          >
            All Time
          </button>

        </div>

        {activeView === "music-insights" && (
          <AnalyticsDashboard analytics={analytics} topTracks={topTracks} topArtists={topArtists} />
        )}

        {activeView === "listening-activity" && (
          <ListeningCharts recentlyPlayed={recentlyPlayed} />
        )}


        {/* TOP CARDS */}

        <section className="top-cards">

          {/* TOP TRACK */}

          {topTracks.length > 0 && (
            <div className="big-card">

              <div className="card-title">
                <span>TOP TRACK</span>
                <span>#1</span>
              </div>

              <div className="track-feature">

                {topTracks[0].image_url && (
                  <img
                    src={topTracks[0].image_url}
                    alt={topTracks[0].album}
                  />
                )}

                <div>
                  <h2>{topTracks[0].name}</h2>
                  <p>{topTracks[0].artist}</p>
                </div>

              </div>

            </div>
          )}


          {/* TOP ARTIST */}

          {topArtists.length > 0 && (
            <div className="big-card">

              <div className="card-title">
                <span>TOP ARTIST</span>
                <span>#1</span>
              </div>

              <div className="artist-feature">

                {topArtists[0].image_url && (
                  <img
                    src={topArtists[0].image_url}
                    alt={topArtists[0].name}
                  />
                )}

                <div>
                  <h2>{topArtists[0].name}</h2>
                  <p>Your most listened-to artist</p>
                </div>

              </div>

            </div>
          )}

        </section>


        {/* CONTENT GRID */}

        <section className="content-grid">


          {/* TOP TRACKS */}

          <div className="panel">

            <div className="panel-header">

              <h2>Top Tracks</h2>

              <span>
                {topTracks.length} tracks
              </span>

            </div>

            <div className="track-list">

              {topTracks.slice(0, 10).map((track, index) => (

                <div
                  className="track-row"
                  key={`${track.name}-${index}`}
                >

                  <span className="rank">
                    {index + 1}
                  </span>

                  {track.image_url && (
                    <img
                      src={track.image_url}
                      alt=""
                    />
                  )}

                  <div className="track-info">

                    <strong>{track.name}</strong>

                    <span>
                      {track.artist}
                    </span>

                  </div>

                </div>

              ))}

            </div>

          </div>


          {/* TOP ARTISTS */}

          <div className="panel">

            <div className="panel-header">

              <h2>Top Artists</h2>

              <span>
                {topArtists.length} artists
              </span>

            </div>

            <div className="artist-list">

              {topArtists.slice(0, 10).map((artist, index) => (

                <div
                  className="artist-row"
                  key={`${artist.name}-${index}`}
                >

                  <span className="rank">
                    {index + 1}
                  </span>

                  {artist.image_url && (
                    <img
                      src={artist.image_url}
                      alt=""
                    />
                  )}

                  <strong>
                    {artist.name}
                  </strong>

                </div>

              ))}

            </div>

          </div>

        </section>


        {/* RECENTLY PLAYED */}

        <section className="panel recent-panel">

          <div className="panel-header">

            <h2>Recently Played</h2>

            <span>
              Latest listening activity
            </span>

          </div>

          <div className="recent-list">

            {recentlyPlayed.slice(0, 10).map((track, index) => (

              <div
                className="recent-row"
                key={`${track.played_at}-${index}`}
              >

                {track.image_url && (
                  <img
                    src={track.image_url}
                    alt=""
                  />
                )}

                <div className="track-info">

                  <strong>{track.name}</strong>

                  <span>
                    {track.artist} • {track.album}
                  </span>

                </div>

                <span className="played-time">
                  {new Date(track.played_at).toLocaleTimeString(
                    [],
                    {
                      hour: "numeric",
                      minute: "2-digit",
                    }
                  )}
                </span>

              </div>

            ))}

          </div>

        </section>

      </main>

    </div>
  );
}

export default App;