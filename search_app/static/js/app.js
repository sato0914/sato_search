// 折りたたみヘッダーのトグル
document.getElementById("headerToggle").onclick = function() {
    var headerContent = document.getElementById("headerContent");
    headerContent.style.display = headerContent.style.display === "none" ? "block" : "none";
};

// 既存の検索フォーム処理
document.getElementById('searchForm').addEventListener('submit', function(e) {
    e.preventDefault(); // デフォルトのフォーム送信をキャンセル

    const formData = $(this).serialize(); // フォームデータをシリアライズ

    // AJAXリクエストを送信（商品検索）
    fetch(`/api/search/?${formData}`)
        .then(response => response.json())
        .then(data => {
            const resultsList = document.getElementById('searchResults');
            resultsList.innerHTML = ''; // 以前の検索結果をクリア

            if (data.length > 0) {
                // 検索結果をリストに追加
                data.forEach(item => {
                    const li = document.createElement('li');
                    // 金額を整数に変換して表示
                    const price = Math.floor(item.price);  // 小数点以下を切り捨て
                    li.textContent = `${item.name} - ${price}円`;
                    resultsList.appendChild(li);
                });
            } else {
                const li = document.createElement('li');
                li.textContent = '結果が見つかりませんでした。';
                resultsList.appendChild(li);
            }
        })
        .catch(error => console.error('Error:', error));
});