// Общий подвал получает текущий год после загрузки документа.
const yearElement = document.getElementById("current-year");
if (yearElement) {
  yearElement.textContent = new Date().getFullYear();
}
