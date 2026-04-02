// Toggle nav state based on auth token
(function () {
    const token = localStorage.getItem('token');
    const authNav = document.getElementById('authNav');
    const userNav = document.getElementById('userNav');

    if (token) {
        if (authNav) authNav.style.display = 'none';
        if (userNav) userNav.style.display = 'flex';
    } else {
        if (authNav) authNav.style.display = 'flex';
        if (userNav) userNav.style.display = 'none';
    }
})();

function logout() {
    localStorage.removeItem('token');
    window.location.href = '/';
}
