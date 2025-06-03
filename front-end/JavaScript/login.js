document.getElementById("loginForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const response = await fetch("http://localhost:5000/login", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
    })
    .then(response => response.json())
    .then(data => {
    if (data.token) {
        // ✅ Save token locally
        localStorage.setItem("jwtToken", data.token);
        // Redirect or show success
        window.location.href = "dashboard.html";
    } else {
        alert(data.error || "Login failed.");
    }
})
.catch(err => alert("Error: " + err));

    const data = await response.json();
    if (data.status === "success") {
        localStorage.setItem("token", data.token);
        alert("Login successful!");
        window.location.href = "dashboard.html";
    } else {
        alert("Login failed: " + data.message);
    }
});
