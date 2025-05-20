// トップ巻物表示
document.addEventListener('DOMContentLoaded', function() {
  const firstScreen = document.querySelector('.first-screen');
  function hideFirstScreen() {
    firstScreen.classList.add('turn-page');  // 新しいアニメーションクラスを追加
    // アニメーション終了後に要素を非表示にする
    firstScreen.addEventListener('animationend', () => {
        firstScreen.style.display = 'none';
    });
  }
  firstScreen.addEventListener('click', hideFirstScreen);
  // 5秒後に非表示にする
  setTimeout(hideFirstScreen, 5000);
});
// トップ巻物表示