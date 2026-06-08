const toggle = document.querySelector('.nav-toggle');
const links = document.querySelector('.nav-links');
const year = document.querySelector('#year');

toggle.addEventListener('click', () => {
  links.classList.toggle('active');
});

document.querySelectorAll('.nav-links a').forEach((link) => {
  link.addEventListener('click', () => links.classList.remove('active'));
});

year.textContent = new Date().getFullYear();

