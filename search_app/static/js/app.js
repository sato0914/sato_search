document.addEventListener("DOMContentLoaded", () => {
    // ハンバーガーメニューの処理
    const hamburgerMenu = document.getElementById("hamburgerMenu");
    const headerContent = document.getElementById("headerContent");

    if (hamburgerMenu && headerContent) {
        hamburgerMenu.addEventListener("click", () => {
            const isVisible = headerContent.style.display === "block";
            headerContent.style.display = isVisible ? "none" : "block";
        });
    }

    // 既存の検索フォーム処理
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function (e) {
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
    }

    // いいねボタンの処理
    const likeButton = document.getElementById('like-button');
    if (likeButton) {
        likeButton.addEventListener('click', function () {
            const productId = likeButton.getAttribute('data-product-id');

            // AJAXリクエストを送信 (POST メソッドを使用)
            fetch(`/like_product/${productId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                },
            })
            .then(response => {
                if (!response.ok) {
                    console.error('Error response:', response);
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // ボタンのテキストといいね数を更新
                if (data.liked) {
                    likeButton.innerText = 'いいね解除';
                } else {
                    likeButton.innerText = 'いいね';
                }
                document.getElementById('likes-count').innerText = `${data.likes_count} いいね`;
            })
            .catch(error => {
                console.error('Error:', error);
            });            
        });
    }
});