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
});
document.addEventListener("DOMContentLoaded", function () {
    const searchModal = document.getElementById("search-modal");
    const openSearchModal = document.getElementById("openSearchModal");
    const closeSearchModal = document.querySelector(".close-modal-btn");

    // 検索ボタンをクリックしたとき
    openSearchModal.addEventListener("click", function () {
        searchModal.style.display = "flex";  // モーダルを表示
    });

    // モーダルの閉じるボタンをクリックしたとき
    closeSearchModal.addEventListener("click", function () {
        searchModal.style.display = "none";  // モーダルを非表示
    });

    // モーダルの外側をクリックしたとき
    searchModal.addEventListener("click", function (e) {
        if (e.target === searchModal) {
            searchModal.style.display = "none";  // モーダルを非表示
        }
    });
});

document.addEventListener('click', function (e) {
    if (e.target.matches('.like-button')) {
        e.preventDefault();
        const url = e.target.dataset.url;
        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.liked) {
                e.target.textContent = 'いいね解除';
            } else {
                e.target.textContent = 'いいね';
            }
            e.target.nextElementSibling.textContent = `${data.like_count} いいね`;
        });
    }
});
