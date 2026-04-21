const form = document.getElementById('registrationForm');
form.addEventListener('submit', function(e) {
    document.getElementById('usernameHelp').textContent = '';
    document.getElementById('emailHelp').textContent = '';
    document.getElementById('passwordHelp').textContent = '';

    let valid = true;

    const username = document.getElementById('username').value;
    if(username.length < 5){
    document.getElementById('usernameHelp').textContent = 'Username must be at least 5 characters.';
    valid = false;
    }

    const password = document.getElementById('password').value;
    if(password.length < 7){
    document.getElementById('passwordHelp').textContent = 'Password must be at least 7 characters.';
    valid = false;
    }

    const email = document.getElementById('email').value;
    if(!email){
    document.getElementById('emailHelp').textContent = 'Email is required.';
    valid = false;
    }

    if (!valid) {
        e.preventDefault()
        console.log(123)
    }
});