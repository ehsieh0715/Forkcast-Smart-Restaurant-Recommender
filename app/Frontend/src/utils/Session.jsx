export async function getOrCreateSession(userId) {
  try {
    const sessionResponse = await fetch(
      `${import.meta.env.VITE_API_URL}/comparison/user/${userId}/sessions`,
      {
        method: "GET",
        headers: { "content-type": "application/json" },
      },
    );

    let data = await sessionResponse.json();
    let sessionId;

    if (data.sessions.length === 0) {
      const createSession = await fetch(
        `${import.meta.env.VITE_API_URL}/comparison/session/create`,
        {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ user_id: userId }),
        },
      );

      const created = await createSession.json();
      sessionId = created.session_id;
    } else {
      sessionId = data.sessions[0].session_id;
    }

    localStorage.setItem("sessionId", sessionId);
    return sessionId;
  } catch (err) {
    throw new Error("Session handling failed: " + err.message);
  }
}
