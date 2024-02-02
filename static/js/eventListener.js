function setCookies(name) {
  // Get the entered data
  const NAME = document.getElementById(name).value;

  // Save the data to a cookie
  document.cookie =
    name + '=' + NAME + '; expires=Thu, 31 Dec 2026 12:00:00 UTC; path=/';

  // Show a message to indicate that the data has been saved
  alert(' ' + name + ' : ' + getCookie(name));
  location.href = '/';
}

function getCookie(name) {
  var value = document.cookie.match('(^|;) ?' + name + '=([^;]*)(;|$)');
  return value ? value[2] : null;
}
// function printCookie_name() {
//   const cookieValue = document.cookie
//     .split('; ')
//     .find((row) => row.startsWith('NAME='))
//     .split('=')[1];

//   // Display the value of the cookie on the page
//   const cookieValueElem = document.getElementById('cookie-value');
//   cookieValueElem.textContent = cookieValue || 'No cookie found.';
// }

// function printCookie_insta_info() {
//   const cookieValue = document.cookie
//     .split('; ')
//     .find((row) => row.startsWith('NAME='))
//     .split('=')[1];

//   // Display the value of the cookie on the page
//   const cookieValueElem = document.getElementById('cookie-value');
//   cookieValueElem.textContent = cookieValue || 'No cookie found.';
// }

// function printCookie_faceinfo() {
//   const cookieValue = document.cookie
//     .split('; ')
//     .find((row) => row.startsWith('NAME='))
//     .split('=')[1];

//   // Display the value of the cookie on the page
//   const cookieValueElem = document.getElementById('cookie-value');
//   cookieValueElem.textContent = cookieValue || 'No cookie found.';
// }
