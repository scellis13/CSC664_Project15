const express = require('express')
const app = express()
const path = require('path')
const {spawn} = require('child_process')

//Enter: lsof -i tcp:'portspecified' into terminal to find node pid
//Enter: kill -9 PID
//Enter: hostname -I to get the LAN IP Address
const execSync = require('child_process').execSync;
const ipstring = execSync('hostname -I', {encoding: 'utf-8' });
const ip = ipstring.trim()
//const ip = '192.168.1.7' // Manually enter ip address
const port = 8000

const crypto = require('crypto')
hash = crypto.getHashes()

const fs = require('fs')

//Objects to pass back to req:
//var sortBy = 0 BTF, 1 IDF, 2 SVD

app.use(express.urlencoded({extended: false}))
app.use(express.static(path.join(__dirname, "public")))
app.use('/images', express.static('photos'))
app.use('/css', express.static('css'))
app.set("view engine", "ejs")
app.set("views", path.join(__dirname, "views"))

app.get('/', (req, res) => {
	console.log('Basic: ', req.body.sort_basic)
	console.log('IDF: ', req.body.sort_idf)
	console.log('SVD: ', req.body.sort_svd)
	console.log('synsetOption: ', req.body.synsetOption)
	urlCount = 0
	res.render("index", {
		searching: false,
		synsetOption: 'None',
		searchQueryChoice: 0,
		tokenChoice: 0,
		query: "",
		sortedBy: "Basic Term Frequency",
		sort_basic: 1,
		sort_idf: 0,
		sort_svd: 0,
		queryDisplay: "",
		urlCount: urlCount,
		histogramDisplay: ""
	})
})
app.post("/queryresult", (req, res) => {
	console.log('Basic: ', req.body.sort_basic)
	console.log('IDF: ', req.body.sort_idf)
	console.log('SVD: ', req.body.sort_svd)
	var query = req.body.query
	if(query === ''){
		queryDisplay = ""
	} else {
		console.log("Calling postData()")
		queryDisplay = "You searched for: " + req.body.query
		callSpawn(req, res, query)
	}
})

app.listen(port, ip, () => {
	console.log('Server running at http://'+ip+':'+port+'/')
})

function callSpawn(req, res, query){
	console.log('synsetOption: ', req.body.synsetOption)
	console.log('req.body.searchQueryChoice: ', req.body.searchQueryChoice)
	console.log('req.body.tokenChoice: ', req.body.tokenChoice)
	if(req.body.sort_basic == 1){
		sortedBy = "Basic Term Frequency"
	} else if(req.body.sort_idf == 1){
		sortedBy = "Inverse Document Frequency"
	} else if(req.body.sort_svd == 1){
		sortedBy = "Singular Value Decomposition"
	} else {
		sortedBy = "Basic Term Frequency"
	}
	
	var synset_option
	
	switch (req.body.synsetOption){
		case "Hypernyms":
			synset_option = 1
			break;
		case "Hyponyms":
			synset_option = 2
			break;
		case "Holonyms":
			synset_option = 3
			break;
		case "Meronyms":
			synset_option = 4
			break;
		case "All":
			synset_option = 5
			break;
		default:
			synset_option = 0
	}
	
	var search_query_choice
	
	switch (parseInt(req.body.searchQueryChoice)){
		case 1:
			search_query_choice = 1
			break;
		case 2:
			search_query_choice = 2
			break;
		default:
			search_query_choice = 0
	}
	
	var token_choice
	
	switch (parseInt(req.body.tokenChoice)){
		case 1:
			token_choice = 1
			break;
		case 2:
			token_choice = 2
			break;
		default:
			token_choice = 0
	}
	
	console.log('req.body.searchQueryChoice: ', search_query_choice)
	console.log('req.body.tokenChoice: ', token_choice)

	var largeDataSet = [];
	hashPwd = crypto.createHash('sha1').update(req.ip).digest('hex');

	let filename = 'queryFiles/'+hashPwd+'.txt'
	console.log("Opening File: ", filename)
	spawn('python', ['python/wordnet_test.py',query,hashPwd, synset_option, search_query_choice, token_choice]).on('exit', (code) => { 
		console.log('Child process closed all stdio with code ${code}');
		
		let rawdata = fs.readFileSync(filename)
		let json_data = JSON.parse(rawdata)
		var urlCount = Object.keys(json_data).length-1;
		console.log('urlCount: ' + urlCount)
		var i
		for(i = 0; i < urlCount; i++){
			console.log('json_data['+i+']: ' + json_data[i])
			json_data[i].sort(function(a, b){
				return b.count - a.count;
			})
		}
		
		json_data[urlCount].sort(function(a, b){
			return b.total_count - a.total_count;
		})
		
		res.render("index", {
			searching: true,
			synsetOption: req.body.synsetOption,
			searchQueryChoice: search_query_choice,
			tokenChoice: token_choice,
			sortedBy: sortedBy,
			sort_basic: req.body.sort_basic,
			sort_idf: req.body.sort_idf,
			sort_svd: req.body.sort_svd,
			query: req.body.query,
			urlCount: urlCount,
			queryDisplay: json_data,
			histogramDisplay: ""
		})

		cleanup_file(filename)
	});
	
}

function cleanup_file(filename){
	console.log("Closing File: ", filename)
}
