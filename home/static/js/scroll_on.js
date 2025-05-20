//scroll_effect
  $(function(){

  });

  $(window).on('load scroll', function(){
    scroll_up_animation(-50);
  });

  function scroll_up_animation(triggerMargin){
    var scrollAnimationElm = document.querySelectorAll('.scroll_up');

    // console.log("animation")

      for (var i = 0; i < scrollAnimationElm.length; i++) {
        // console.log("No.:" + i + ", top:" + scrollAnimationElm[i].getBoundingClientRect().top + ", height:" + window.innerHeight);
        if (window.innerHeight > scrollAnimationElm[i].getBoundingClientRect().top + triggerMargin) {
          scrollAnimationElm[i].classList.add('on');
        }
      }
  }


//スクロールした時に処理を実行
window.addEventListener('scroll', function(){
  //トップへ戻るボタンを取得
  let topBtn = document.querySelector('.form_button');
  //画面上部からトップビジュアル下の位置取得
  const topVisual = document.querySelector('.wrapper_hp').getBoundingClientRect().bottom;
  //トップビジュアル下の位置より下にスクロールされたらactive
  if(topVisual <= 0){
    topBtn.classList.add('active');
  } else {
    topBtn.classList.remove('active');
  }
  //ドキュメントの高さ
  const scrollHeight = document.body.clientHeight;
  //スクロール位置
  const scrollPosition = window.scrollY || window;
  //windowの高さ
  const windowHeight = window.innerHeight;
  //footer取得
  const footer = document.querySelector('footer');
  // footerの高さ
  const footerHeight = footer.offsetHeight;
  // フッター位置から少し上の位置を指定
  if (scrollHeight - (scrollPosition + windowHeight) <= footerHeight * 1.8) {
    topBtn.classList.add('stop');
  } else {
    topBtn.classList.remove('stop');
  }
});
