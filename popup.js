document.getElementById("parse").addEventListener("click", async () => {
    let sitemapUrl = document.getElementById("sitemap_url").value;
    let startDate = document.getElementById("start_date").value;
    let endDate = document.getElementById("end_date").value;
    let contentType = document.getElementById("content_type").value;

    if (!sitemapUrl) {
        alert("Please enter a sitemap URL");
        return;
    }

    document.getElementById("result_text").textContent = "Processing...";

    const response = await fetch("http://127.0.0.1:8000/parse_sitemap", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            sitemap_url: sitemapUrl,
            start_date: startDate,
            end_date: endDate,
            content_filter: contentType
        })
    });

    let result = await response.json();
    document.getElementById("result_text").textContent = JSON.stringify(result, null, 2);
});
