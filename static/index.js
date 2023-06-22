$.get('/getNews', function (data) {
    var size = Object.keys(data['title']).length;
    console.log(data)
    for (var i = 0; i < size; i++) {
        const newsCont = document.getElementById('newsCont')
        const row = document.createElement('div')
        row.className = 'row'
        row.style.backgroundImage = "url("+data['img'][i]+")"
        const newsHead = document.createElement('div');
        newsHead.className = 'newsHead';
        const title = document.createElement('h3')
        const description = document.createElement('p')
        title.className = 'title';
        description.className = 'desc'
        title.innerHTML = data['title'][i]
        description.innerHTML = data['desc'][i]
        newsHead.appendChild(title)
        newsHead.appendChild(description)
        const newsUrl = document.createElement('a');  
        newsUrl.href = data['link'][i]
        row.appendChild(newsHead)
        newsUrl.appendChild(row);
        newsCont.appendChild(newsUrl)
    }
}); 
