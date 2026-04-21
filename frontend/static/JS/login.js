const form = document.getElementById('loginForm');
form.addEventListener('submit', async function(e) {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    const response = await fetch("/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            email: email,
            password: password
        })
    });

    const data = await response.json()
    console.log(data)

    if ("login_error" in data) {
        console.log("Error loging in!")
        document.getElementById("error_message").style.display = "block";
    } else {
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("refresh_token", data.refresh_token);
        window.location = '/'
    }
});