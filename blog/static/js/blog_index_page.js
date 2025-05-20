// document.addEventListener("DOMContentLoaded", function () {
//   const pageLinks = document.querySelectorAll(
//     ".page a:not(.page-prev):not(.page-next)"
//   );

//   pageLinks.forEach((link) => {
//     link.addEventListener("click", function (event) {
//       event.preventDefault(); // ページ遷移を防ぐ

//       // すべてのページ番号から 'current' クラスを削除
//       pageLinks.forEach((l) => l.classList.remove("current"));

//       // クリックされたページに 'current' クラスを追加
//       this.classList.add("current");
//     });
//   });
// });
