import { useEffect, useState } from "react";
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

function App() {
  const [user, setUser] = useState(null);
  const [topTracks, setTopTracks] = useState([]);
  const [topArtists, setTopArtists] = useState([]);
  const [recentlyPlayed, setRecentlyPlayed] = useState([]);

  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState(false);

  useEffect(() => {
    loadDashboard();
  }, []);

  async function loadDashboard() {
    try {
      const [
        userResponse,
        tracksResponse,
        artistsResponse,
        recentResponse,
      ] = await Promise.all([
        fetch(`${API_URL}/me`),
        fetch(`${API_URL}/top-tracks`),
        fetch(`${API_URL}/top-artists`),
        fetch(`${API_URL}/recently-played`),
      ]);

      const userData = await userResponse.json();
      const tracksData = await tracksResponse.json();
      const artistsData = await artistsResponse.json();
      const recentData = await recentResponse.json();

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

    } catch (error) {
      console.error("Dashboard loading error:", error);
    } finally {
      setLoading(false);
    }
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
    <div className="dashboard">

      {/* SIDEBAR */}

      <aside className="sidebar">

        <div className="sidebar-logo">
          <StatifyLogo />
          <span>STATIFY</span>
        </div>

        <nav>
          <a className="active">Overview</a>
          <a>Music Insights</a>
          <a>Listening Activity</a>
        </nav>

      </aside>


      {/* MAIN CONTENT */}

      <main className="main-content">

        {/* HEADER */}

        <header className="dashboard-header">

          <div>
            <p className="eyebrow">YOUR MUSIC</p>

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

          <button>4 Weeks</button>

          <button className="selected">
            6 Months
          </button>

          <button>All Time</button>

        </div>


        {/* TOP CARDS */}

        <section className="top-cards">

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