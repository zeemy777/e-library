# Catalogue metadata for the demo library.
# Every book uses a public-domain or openly licensed edition
# so the files can be stored and shared with the project.

CATEGORIES = [
    {
        "name": "Technology",
        "description": "Programming, software engineering, data and computing.",
        "allow_download": True
    },
    {
        "name": "Science",
        "description": "Natural sciences, astronomy and the scientific method.",
        "allow_download": True
    },
    {
        "name": "Business",
        "description": "Entrepreneurship, economics, money and management.",
        "allow_download": True
    },
    {
        "name": "Literature",
        "description": "Novels, short stories and poetry from around the world.",
        "allow_download": True
    },
    {
        "name": "Fantasy",
        "description": "Magic, myths, fairy tales and imagined worlds.",
        "allow_download": True
    },
    {
        "name": "Mathematics",
        "description": "Pure and applied mathematics for every level.",
        "allow_download": True
    },
    {
        "name": "History",
        "description": "World history, civilisations and political thought.",
        "allow_download": True
    },
    {
        "name": "Open Media",
        "description": "Open-licence films and sample video clips.",
        "allow_download": True
    }
]


BOOKS = [
    {
        "slug": "think-python-2e",
        "title": "Think Python: How to Think Like a Computer Scientist",
        "author": "Allen B. Downey",
        "publisher": "Green Tea Press",
        "category": "Technology",
        "description": (
            "A clear, practical introduction to Python for complete "
            "beginners, covering variables, functions, data structures, "
            "objects and debugging through short exercises."
        ),
        "source": "url",
        "url": "https://greenteapress.com/thinkpython2/thinkpython2.pdf",
        "cover_url": "https://greenteapress.com/covers/think_python_cover.jpeg"
    },
    {
        "slug": "think-stats-2e",
        "title": "Think Stats: Exploratory Data Analysis in Python",
        "author": "Allen B. Downey",
        "publisher": "Green Tea Press",
        "category": "Technology",
        "description": (
            "Exploratory data analysis for programmers: distributions, "
            "probability, hypothesis testing and regression using real "
            "datasets in Python."
        ),
        "source": "url",
        "url": "https://greenteapress.com/thinkstats2/thinkstats2.pdf",
        "cover_url": "https://greenteapress.com/covers/think_stats_cover.jpeg"
    },
    {
        "slug": "think-dsp",
        "title": "Think DSP: Digital Signal Processing in Python",
        "author": "Allen B. Downey",
        "publisher": "Green Tea Press",
        "category": "Technology",
        "description": (
            "A hands-on introduction to digital signal processing with "
            "Python, from sound waves and spectra to filters and sampling."
        ),
        "source": "url",
        "url": "https://greenteapress.com/thinkdsp/thinkdsp.pdf",
        "cover_url": "https://greenteapress.com/covers/think_dsp_cover.jpeg"
    },
    {
        "slug": "think-os",
        "title": "Think OS: A Brief Introduction to Operating Systems",
        "author": "Allen B. Downey",
        "publisher": "Green Tea Press",
        "category": "Technology",
        "description": (
            "A short, approachable tour of operating-system concepts: "
            "processes, threads, virtual memory, file systems and "
            "concurrency."
        ),
        "source": "url",
        "url": "https://greenteapress.com/thinkos/thinkos.pdf"
    },
    {
        "slug": "think-complexity-2e",
        "title": "Think Complexity: Complexity Science and Computational Modeling",
        "author": "Allen B. Downey",
        "publisher": "Green Tea Press",
        "category": "Technology",
        "description": (
            "Explores complexity science through computational models such "
            "as cellular automata, small-world networks and self-organised "
            "criticality."
        ),
        "source": "url",
        "url": "https://greenteapress.com/thinkcomplexity2/thinkcomplexity2.pdf",
        "cover_url": "https://greenteapress.com/covers/think_complexity_cover.jpeg"
    },
    {
        "slug": "pro-git",
        "title": "Pro Git: Everything You Need to Know About Git",
        "author": "Scott Chacon and Ben Straub",
        "publisher": "Apress",
        "category": "Technology",
        "description": (
            "The complete guide to Git, from basic snapshots and branching "
            "to distributed workflows and maintaining a repository."
        ),
        "source": "url",
        "url": (
            "https://github.com/progit/progit2/releases/download/"
            "2.1.436/progit.pdf"
        )
    },
    {
        "slug": "origin-of-species",
        "title": "On the Origin of Species",
        "author": "Charles Darwin",
        "publisher": "John Murray",
        "category": "Science",
        "description": (
            "Darwin's foundational work on evolution by natural selection, "
            "drawn from decades of observation in the natural world."
        ),
        "source": "gutenberg",
        "gid": 1228
    },
    {
        "slug": "relativity",
        "title": "Relativity: The Special and General Theory",
        "author": "Albert Einstein",
        "publisher": "Methuen & Co.",
        "category": "Science",
        "description": (
            "Einstein's own accessible account of special and general "
            "relativity, written for readers without advanced mathematics."
        ),
        "source": "gutenberg",
        "gid": 30155
    },
    {
        "slug": "voyage-of-the-beagle",
        "title": "The Voyage of the Beagle",
        "author": "Charles Darwin",
        "publisher": "Henry Colburn",
        "category": "Science",
        "description": (
            "Darwin's travel journal from the five-year voyage that shaped "
            "his theory of evolution."
        ),
        "source": "gutenberg",
        "gid": 944
    },
    {
        "slug": "astronomy-for-amateurs",
        "title": "Astronomy for Amateurs",
        "author": "Camille Flammarion",
        "publisher": "D. Appleton and Company",
        "category": "Science",
        "description": (
            "A classic popular guide to the night sky, the planets, the Sun "
            "and the stars, written for curious beginners."
        ),
        "source": "gutenberg",
        "gid": 25267
    },
    {
        "slug": "wealth-of-nations",
        "title": "The Wealth of Nations",
        "author": "Adam Smith",
        "publisher": "W. Strahan and T. Cadell",
        "category": "Business",
        "description": (
            "Adam Smith's landmark study of markets, labour, trade and the "
            "invisible forces that shape national prosperity."
        ),
        "source": "gutenberg",
        "gid": 3300
    },
    {
        "slug": "science-of-getting-rich",
        "title": "The Science of Getting Rich",
        "author": "Wallace D. Wattles",
        "publisher": "Elizabeth Towne",
        "category": "Business",
        "description": (
            "A 1910 classic on purposeful thinking, personal initiative and "
            "building wealth through value creation."
        ),
        "source": "gutenberg",
        "gid": 59844
    },
    {
        "slug": "art-of-money-getting",
        "title": "The Art of Money Getting",
        "author": "P. T. Barnum",
        "publisher": "F. J. Drake & Co.",
        "category": "Business",
        "description": (
            "P. T. Barnum's practical nineteenth-century rules for earning, "
            "saving and keeping money."
        ),
        "source": "gutenberg",
        "gid": 8581
    },
    {
        "slug": "pride-and-prejudice",
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "publisher": "T. Egerton",
        "category": "Literature",
        "description": (
            "Elizabeth Bennet navigates family, first impressions and an "
            "unexpected romance in Austen's best-loved novel."
        ),
        "source": "gutenberg",
        "gid": 1342
    },
    {
        "slug": "moby-dick",
        "title": "Moby-Dick",
        "author": "Herman Melville",
        "publisher": "Harper & Brothers",
        "category": "Literature",
        "description": (
            "A young sailor joins the whaling ship Pequod and is drawn into "
            "Captain Ahab's obsessive hunt for the white whale."
        ),
        "source": "gutenberg",
        "gid": 2701
    },
    {
        "slug": "the-great-gatsby",
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "publisher": "Charles Scribner's Sons",
        "category": "Literature",
        "description": (
            "Jay Gatsby's glittering parties conceal a longing for the past "
            "in Fitzgerald's portrait of the American Jazz Age."
        ),
        "source": "gutenberg",
        "gid": 64317
    },
    {
        "slug": "frankenstein",
        "title": "Frankenstein; Or, The Modern Prometheus",
        "author": "Mary Wollstonecraft Shelley",
        "publisher": "Lackington, Hughes, Harding, Mavor & Jones",
        "category": "Literature",
        "description": (
            "A young scientist creates life and must confront the "
            "consequences in the novel that founded modern science fiction."
        ),
        "source": "gutenberg",
        "gid": 84
    },
    {
        "slug": "dracula",
        "title": "Dracula",
        "author": "Bram Stoker",
        "publisher": "Archibald Constable and Company",
        "category": "Literature",
        "description": (
            "Letters, diaries and newspaper clippings trace a terrifying "
            "journey from Transylvania to London in Stoker's gothic classic."
        ),
        "source": "gutenberg",
        "gid": 345
    },
    {
        "slug": "jane-eyre",
        "title": "Jane Eyre",
        "author": "Charlotte Brontë",
        "publisher": "Smith, Elder & Co.",
        "category": "Literature",
        "description": (
            "An orphaned governess finds independence, love and a dark "
            "secret at Thornfield Hall."
        ),
        "source": "gutenberg",
        "gid": 1260
    },
    {
        "slug": "picture-of-dorian-gray",
        "title": "The Picture of Dorian Gray",
        "author": "Oscar Wilde",
        "publisher": "Ward, Lock & Co.",
        "category": "Literature",
        "description": (
            "A beautiful portrait ages while its subject stays young, in "
            "Wilde's witty study of vanity and corruption."
        ),
        "source": "gutenberg",
        "gid": 174
    },
    {
        "slug": "the-time-machine",
        "title": "The Time Machine",
        "author": "H. G. Wells",
        "publisher": "William Heinemann",
        "category": "Literature",
        "description": (
            "A Victorian inventor travels to the distant future and finds "
            "humanity divided into two strange species."
        ),
        "source": "gutenberg",
        "gid": 35
    },
    {
        "slug": "alices-adventures-in-wonderland",
        "title": "Alice's Adventures in Wonderland",
        "author": "Lewis Carroll",
        "publisher": "Macmillan",
        "category": "Literature",
        "description": (
            "Alice follows a white rabbit into a world of riddles, strange "
            "creatures and a very unreasonable queen."
        ),
        "source": "gutenberg",
        "gid": 11
    },
    {
        "slug": "the-prophet",
        "title": "The Prophet",
        "author": "Kahlil Gibran",
        "publisher": "Alfred A. Knopf",
        "category": "Literature",
        "description": (
            "Kahlil Gibran's poetic meditations on love, work, freedom, joy "
            "and sorrow, told through the voice of a departing sage."
        ),
        "source": "gutenberg",
        "gid": 58585
    },
    {
        "slug": "the-metamorphosis",
        "title": "The Metamorphosis",
        "author": "Franz Kafka",
        "publisher": "Kurt Wolff Verlag",
        "category": "Literature",
        "description": (
            "Kafka's unsettling novella about a travelling salesman who "
            "wakes one morning transformed into a giant insect."
        ),
        "source": "gutenberg",
        "gid": 5200
    },
    {
        "slug": "heart-of-darkness",
        "title": "Heart of Darkness",
        "author": "Joseph Conrad",
        "publisher": "Blackwood's Magazine",
        "category": "Literature",
        "description": (
            "Conrad's haunting voyage up the Congo River, a study of "
            "colonialism, greed and the darkness within."
        ),
        "source": "gutenberg",
        "gid": 219
    },
    {
        "slug": "calculus-made-easy",
        "title": "Calculus Made Easy",
        "author": "Silvanus P. Thompson",
        "publisher": "Macmillan",
        "category": "Mathematics",
        "description": (
            "Thompson's friendly classic that makes calculus intuitive, "
            "using plain language and everyday examples."
        ),
        "source": "url",
        "url": "https://archive.org/download/ost-math-33283-pdf/33283-pdf.pdf",
        "cover_url": (
            "https://www.gutenberg.org/cache/epub/33283/"
            "pg33283.cover.medium.jpg"
        )
    },
    {
        "slug": "flatland",
        "title": "Flatland: A Romance of Many Dimensions",
        "author": "Edwin A. Abbott",
        "publisher": "Seeley & Co.",
        "category": "Mathematics",
        "description": (
            "A mathematical satire set in a two-dimensional world, "
            "exploring dimensions, society and the limits of perception."
        ),
        "source": "gutenberg",
        "gid": 201
    },
    {
        "slug": "introduction-to-statistical-learning",
        "title": "An Introduction to Statistical Learning",
        "author": "Gareth James, Daniela Witten, Trevor Hastie and Robert Tibshirani",
        "publisher": "Springer",
        "category": "Mathematics",
        "description": (
            "A modern introduction to statistical learning with practical "
            "examples in R, covering regression, classification, resampling "
            "and trees."
        ),
        "source": "url",
        "url": "https://www.statlearning.com/s/ISLRSeventhPrinting.pdf"
    },
    {
        "slug": "the-story-of-mankind",
        "title": "The Story of Mankind",
        "author": "Hendrik Willem van Loon",
        "publisher": "Boni & Liveright",
        "category": "History",
        "description": (
            "Van Loon's Newbery-winning history of humanity, told as a "
            "lively story from prehistory to the twentieth century."
        ),
        "source": "gutenberg",
        "gid": 754
    },
    {
        "slug": "history-of-herodotus",
        "title": "The History of Herodotus",
        "author": "Herodotus",
        "publisher": "J. M. Dent & Sons",
        "category": "History",
        "description": (
            "The founding work of history in the Western tradition, "
            "recounting the rise of Persia and the Greek city-states."
        ),
        "source": "gutenberg",
        "gid": 2707
    },
    {
        "slug": "the-prince",
        "title": "The Prince",
        "author": "Niccolò Machiavelli",
        "publisher": "Antonio Blado",
        "category": "History",
        "description": (
            "Machiavelli's enduring manual on political power, statecraft "
            "and the realities of ruling."
        ),
        "source": "gutenberg",
        "gid": 1232
    },
    {
        "slug": "adventures-of-sherlock-holmes",
        "title": "The Adventures of Sherlock Holmes",
        "author": "Arthur Conan Doyle",
        "publisher": "George Newnes",
        "category": "Literature",
        "description": (
            "Twelve celebrated cases of the world's most famous consulting "
            "detective, narrated by his loyal friend Dr. Watson."
        ),
        "source": "gutenberg",
        "gid": 1661
    },
    {
        "slug": "a-tale-of-two-cities",
        "title": "A Tale of Two Cities",
        "author": "Charles Dickens",
        "publisher": "Chapman & Hall",
        "category": "Literature",
        "description": (
            "Dickens's novel of love, sacrifice and revolution, moving "
            "between London and Paris in the years of the Terror."
        ),
        "source": "gutenberg",
        "gid": 98
    },
    {
        "slug": "great-expectations",
        "title": "Great Expectations",
        "author": "Charles Dickens",
        "publisher": "Chapman & Hall",
        "category": "Literature",
        "description": (
            "The orphan Pip's journey from the Kent marshes to London "
            "society, and what he learns about loyalty and ambition."
        ),
        "source": "gutenberg",
        "gid": 1400
    },
    {
        "slug": "treasure-island",
        "title": "Treasure Island",
        "author": "Robert Louis Stevenson",
        "publisher": "Cassell & Co.",
        "category": "Literature",
        "description": (
            "The classic tale of pirates, buried gold and young Jim "
            "Hawkins's voyage with the unforgettable Long John Silver."
        ),
        "source": "gutenberg",
        "gid": 120
    },
    {
        "slug": "jekyll-and-hyde",
        "title": "The Strange Case of Dr. Jekyll and Mr. Hyde",
        "author": "Robert Louis Stevenson",
        "publisher": "Longmans, Green & Co.",
        "category": "Literature",
        "description": (
            "A gripping novella about a respectable doctor and the dark "
            "double that his experiments release on Victorian London."
        ),
        "source": "gutenberg",
        "gid": 43
    },
    {
        "slug": "the-war-of-the-worlds",
        "title": "The War of the Worlds",
        "author": "H. G. Wells",
        "publisher": "William Heinemann",
        "category": "Literature",
        "description": (
            "The founding novel of alien invasion fiction, in which "
            "Martian machines bring chaos to the English countryside."
        ),
        "source": "gutenberg",
        "gid": 36
    },
    {
        "slug": "wuthering-heights",
        "title": "Wuthering Heights",
        "author": "Emily Brontë",
        "publisher": "Thomas Cautley Newby",
        "category": "Literature",
        "description": (
            "A wild, passionate story of Heathcliff and Catherine set on "
            "the windswept Yorkshire moors."
        ),
        "source": "gutenberg",
        "gid": 768
    },
    {
        "slug": "emma",
        "title": "Emma",
        "author": "Jane Austen",
        "publisher": "John Murray",
        "category": "Literature",
        "description": (
            "Austen's witty comedy about a confident young matchmaker "
            "who misreads the hearts of everyone around her."
        ),
        "source": "gutenberg",
        "gid": 158
    },
    {
        "slug": "little-women",
        "title": "Little Women",
        "author": "Louisa May Alcott",
        "publisher": "Roberts Brothers",
        "category": "Literature",
        "description": (
            "The beloved story of the four March sisters growing up in "
            "New England during and after the American Civil War."
        ),
        "source": "gutenberg",
        "gid": 514
    },
    {
        "slug": "adventures-of-tom-sawyer",
        "title": "The Adventures of Tom Sawyer",
        "author": "Mark Twain",
        "publisher": "American Publishing Company",
        "category": "Literature",
        "description": (
            "Mischief, adventure and buried treasure along the Mississippi "
            "in Twain's classic story of boyhood."
        ),
        "source": "gutenberg",
        "gid": 74
    },
    {
        "slug": "adventures-of-huckleberry-finn",
        "title": "Adventures of Huckleberry Finn",
        "author": "Mark Twain",
        "publisher": "Charles L. Webster and Company",
        "category": "Literature",
        "description": (
            "Huck and Jim's raft journey down the Mississippi, a landmark "
            "of American literature and a sharp look at its society."
        ),
        "source": "gutenberg",
        "gid": 76
    },
    {
        "slug": "crime-and-punishment",
        "title": "Crime and Punishment",
        "author": "Fyodor Dostoyevsky",
        "publisher": "The Russian Messenger",
        "category": "Literature",
        "description": (
            "A psychological masterpiece following a poor former student "
            "in St. Petersburg after he commits a terrible crime."
        ),
        "source": "gutenberg",
        "gid": 2554
    },
    {
        "slug": "wonderful-wizard-of-oz",
        "title": "The Wonderful Wizard of Oz",
        "author": "L. Frank Baum",
        "publisher": "George M. Hill Company",
        "category": "Literature",
        "description": (
            "Dorothy's journey along the yellow brick road with the "
            "Scarecrow, the Tin Woodman and the Cowardly Lion."
        ),
        "source": "gutenberg",
        "gid": 55
    },
    {
        "slug": "peter-pan",
        "title": "Peter Pan",
        "author": "J. M. Barrie",
        "publisher": "Hodder & Stoughton",
        "category": "Literature",
        "description": (
            "The boy who wouldn't grow up whisks Wendy and her brothers "
            "away to Neverland, home of pirates and lost boys."
        ),
        "source": "gutenberg",
        "gid": 16
    },
    {
        "slug": "chemical-history-of-a-candle",
        "title": "The Chemical History of a Candle",
        "author": "Michael Faraday",
        "publisher": "Griffin, Bohn & Co.",
        "category": "Science",
        "description": (
            "Faraday's famous Christmas lectures, explaining combustion "
            "and basic chemistry through the humble candle."
        ),
        "source": "gutenberg",
        "gid": 14474
    },
    {
        "slug": "the-descent-of-man",
        "title": "The Descent of Man",
        "author": "Charles Darwin",
        "publisher": "John Murray",
        "category": "Science",
        "description": (
            "Darwin applies evolutionary theory to human origins and "
            "introduces his theory of sexual selection."
        ),
        "source": "gutenberg",
        "gid": 2300
    },
    {
        "slug": "theory-of-the-leisure-class",
        "title": "The Theory of the Leisure Class",
        "author": "Thorstein Veblen",
        "publisher": "Macmillan",
        "category": "Business",
        "description": (
            "Veblen's sharp economic study that coined the phrase "
            "\"conspicuous consumption\"."
        ),
        "source": "gutenberg",
        "gid": 833
    },
    {
        "slug": "principles-of-political-economy",
        "title": "On the Principles of Political Economy and Taxation",
        "author": "David Ricardo",
        "publisher": "John Murray",
        "category": "Business",
        "description": (
            "Ricardo's foundational work on rent, wages, profit and the "
            "theory of comparative advantage in trade."
        ),
        "source": "gutenberg",
        "gid": 33310
    },
    {
        "slug": "autobiography-of-benjamin-franklin",
        "title": "The Autobiography of Benjamin Franklin",
        "author": "Benjamin Franklin",
        "publisher": "Project Gutenberg",
        "category": "Business",
        "description": (
            "The printer, inventor and statesman's own account of hard "
            "work, thrift and self-improvement."
        ),
        "source": "gutenberg",
        "gid": 20203
    },
    {
        "slug": "essay-on-probabilities",
        "title": "A Philosophical Essay on Probabilities",
        "author": "Pierre-Simon Laplace",
        "publisher": "John Wiley & Sons",
        "category": "Mathematics",
        "description": (
            "Laplace's accessible introduction to probability theory and "
            "how it applies to science and everyday judgement."
        ),
        "source": "gutenberg",
        "gid": 58881
    },
    {
        "slug": "hindu-arabic-numerals",
        "title": "The Hindu-Arabic Numerals",
        "author": "David Eugene Smith and Louis Charles Karpinski",
        "publisher": "Ginn and Company",
        "category": "Mathematics",
        "description": (
            "A history of the digits we use every day, tracing them from "
            "India through the Arab world to Europe."
        ),
        "source": "gutenberg",
        "gid": 22599
    },
    {
        "slug": "the-canterbury-puzzles",
        "title": "The Canterbury Puzzles",
        "author": "Henry Ernest Dudeney",
        "publisher": "Thomas Nelson & Sons",
        "category": "Mathematics",
        "description": (
            "Ingenious mathematical puzzles told through Chaucer's "
            "pilgrims, with full solutions at the end."
        ),
        "source": "gutenberg",
        "gid": 27635
    },
    {
        "slug": "the-romance-of-mathematics",
        "title": "The Romance of Mathematics",
        "author": "P. H. Ditchfield",
        "publisher": "Project Gutenberg",
        "category": "Mathematics",
        "description": (
            "A light-hearted tale showing how mathematics turns up in "
            "everyday life, from shopping to architecture."
        ),
        "source": "gutenberg",
        "gid": 26481
    },
    {
        "slug": "the-art-of-war",
        "title": "The Art of War",
        "author": "Sun Tzu",
        "publisher": "Luzac & Co.",
        "category": "History",
        "description": (
            "The ancient Chinese treatise on strategy, leadership and "
            "conflict, translated by Lionel Giles."
        ),
        "source": "gutenberg",
        "gid": 132
    },
    {
        "slug": "meditations",
        "title": "Meditations",
        "author": "Marcus Aurelius",
        "publisher": "Project Gutenberg",
        "category": "History",
        "description": (
            "The private reflections of a Roman emperor on duty, "
            "self-discipline and Stoic philosophy."
        ),
        "source": "gutenberg",
        "gid": 2680
    },
    {
        "slug": "the-republic",
        "title": "The Republic",
        "author": "Plato",
        "publisher": "Clarendon Press",
        "category": "History",
        "description": (
            "Plato's dialogue on justice and the ideal state, including "
            "the famous allegory of the cave."
        ),
        "source": "gutenberg",
        "gid": 1497
    },
    {
        "slug": "leviathan",
        "title": "Leviathan",
        "author": "Thomas Hobbes",
        "publisher": "Andrew Crooke",
        "category": "History",
        "description": (
            "Hobbes's landmark argument for the social contract and strong "
            "government, written during the English Civil War."
        ),
        "source": "gutenberg",
        "gid": 3207
    },
    {
        "slug": "the-communist-manifesto",
        "title": "The Communist Manifesto",
        "author": "Karl Marx and Friedrich Engels",
        "publisher": "Project Gutenberg",
        "category": "History",
        "description": (
            "The 1848 political pamphlet that shaped a century of "
            "revolutions, debates and political movements."
        ),
        "source": "gutenberg",
        "gid": 61
    },
    {
        "slug": "beyond-good-and-evil",
        "title": "Beyond Good and Evil",
        "author": "Friedrich Nietzsche",
        "publisher": "Project Gutenberg",
        "category": "History",
        "description": (
            "Nietzsche's challenge to traditional morality and his vision "
            "of a philosophy of the future."
        ),
        "source": "gutenberg",
        "gid": 4363
    },
    {
        "slug": "the-problems-of-philosophy",
        "title": "The Problems of Philosophy",
        "author": "Bertrand Russell",
        "publisher": "Williams and Norgate",
        "category": "History",
        "description": (
            "Russell's clear, approachable introduction to knowledge, "
            "reality and the value of philosophical thinking."
        ),
        "source": "gutenberg",
        "gid": 5827
    }
]


VIDEOS = [
    {
        "slug": "python-for-beginners",
        "title": "Python for Beginners — Full Course",
        "author": "freeCodeCamp.org",
        "publisher": "YouTube",
        "category": "Technology",
        "description": (
            "A complete beginner course covering Python syntax, data "
            "structures, functions, files and practical projects."
        ),
        "video_url": "https://www.youtube.com/watch?v=eWRfhZUzrAc",
        "cover_url": "https://img.youtube.com/vi/eWRfhZUzrAc/hqdefault.jpg"
    },
    {
        "slug": "html-css-full-course",
        "title": "HTML and CSS for Beginners — Full Course",
        "author": "freeCodeCamp.org",
        "publisher": "YouTube",
        "category": "Technology",
        "description": (
            "Learn how the web is built: semantic HTML, modern CSS layout, "
            "responsive design and a complete hands-on website project."
        ),
        "video_url": "https://www.youtube.com/watch?v=pQN-pnXPaVg",
        "cover_url": "https://img.youtube.com/vi/pQN-pnXPaVg/hqdefault.jpg"
    },
    {
        "slug": "javascript-full-course",
        "title": "JavaScript Programming — Full Course",
        "author": "freeCodeCamp.org",
        "publisher": "YouTube",
        "category": "Technology",
        "description": (
            "A thorough JavaScript course covering the language, the DOM, "
            "asynchronous code and building interactive web pages."
        ),
        "video_url": "https://www.youtube.com/watch?v=PkZNo7MFNFg",
        "cover_url": "https://img.youtube.com/vi/PkZNo7MFNFg/hqdefault.jpg"
    },
    {
        "slug": "crash-course-computer-science",
        "title": "Computer Science: Crash Course #1",
        "author": "CrashCourse",
        "publisher": "YouTube",
        "category": "Technology",
        "description": (
            "An energetic introduction to how computers represent and "
            "process information, from early machines to modern logic."
        ),
        "video_url": "https://www.youtube.com/watch?v=tpIctyqH29Q",
        "cover_url": "https://img.youtube.com/vi/tpIctyqH29Q/hqdefault.jpg"
    },
    {
        "slug": "crash-course-biology",
        "title": "Biology: Crash Course #1",
        "author": "CrashCourse",
        "publisher": "YouTube",
        "category": "Science",
        "description": (
            "A fast, visual introduction to biology: what life is made of, "
            "how cells work and why biology matters."
        ),
        "video_url": "https://www.youtube.com/watch?v=QnQe0xW_JY4",
        "cover_url": "https://img.youtube.com/vi/QnQe0xW_JY4/hqdefault.jpg"
    },
    {
        "slug": "crash-course-economics",
        "title": "Economics: Crash Course #1",
        "author": "CrashCourse",
        "publisher": "YouTube",
        "category": "Business",
        "description": (
            "An accessible introduction to scarcity, choice and the basic "
            "questions every economy has to answer."
        ),
        "video_url": "https://www.youtube.com/watch?v=3ez10ADR_gM",
        "cover_url": "https://img.youtube.com/vi/3ez10ADR_gM/hqdefault.jpg"
    },
    {
        "slug": "react-full-course",
        "title": "React Course — Beginner's Tutorial",
        "author": "freeCodeCamp.org",
        "publisher": "YouTube",
        "category": "Technology",
        "description": (
            "Learn React from scratch: components, props, state, hooks "
            "and building real projects step by step."
        ),
        "video_url": "https://www.youtube.com/watch?v=bMknfKXIFA8",
        "cover_url": "https://img.youtube.com/vi/bMknfKXIFA8/hqdefault.jpg"
    },
    {
        "slug": "sql-full-course",
        "title": "SQL Tutorial — Full Database Course for Beginners",
        "author": "freeCodeCamp.org",
        "publisher": "YouTube",
        "category": "Technology",
        "description": (
            "Design databases and write SQL queries: tables, keys, joins, "
            "functions and real-world schema examples."
        ),
        "video_url": "https://www.youtube.com/watch?v=HXV3zeQKqGY",
        "cover_url": "https://img.youtube.com/vi/HXV3zeQKqGY/hqdefault.jpg"
    },
    {
        "slug": "git-github-crash-course",
        "title": "Git and GitHub for Beginners — Crash Course",
        "author": "freeCodeCamp.org",
        "publisher": "YouTube",
        "category": "Technology",
        "description": (
            "Version control essentials: commits, branches, merging, pull "
            "requests and collaborating on GitHub."
        ),
        "video_url": "https://www.youtube.com/watch?v=RGOj5yH7evk",
        "cover_url": "https://img.youtube.com/vi/RGOj5yH7evk/hqdefault.jpg"
    },
    {
        "slug": "harvard-cs50-full-course",
        "title": "Harvard CS50 — Full Computer Science Course",
        "author": "freeCodeCamp.org",
        "publisher": "YouTube",
        "category": "Technology",
        "description": (
            "Harvard's famous introduction to computer science, covering "
            "C, algorithms, memory, Python, SQL and the web."
        ),
        "video_url": "https://www.youtube.com/watch?v=8mAITcNt710",
        "cover_url": "https://img.youtube.com/vi/8mAITcNt710/hqdefault.jpg"
    },
    {
        "slug": "c-programming-tutorial",
        "title": "C Programming Tutorial for Beginners",
        "author": "freeCodeCamp.org",
        "publisher": "YouTube",
        "category": "Technology",
        "description": (
            "A beginner-friendly C course: variables, conditionals, loops, "
            "arrays, pointers, structs and files."
        ),
        "video_url": "https://www.youtube.com/watch?v=KJgsSFOSQv0",
        "cover_url": "https://img.youtube.com/vi/KJgsSFOSQv0/hqdefault.jpg"
    },
    {
        "slug": "data-structures-course",
        "title": "Data Structures — Easy to Advanced Course",
        "author": "freeCodeCamp.org",
        "publisher": "YouTube",
        "category": "Technology",
        "description": (
            "Arrays, linked lists, stacks, queues, trees, heaps and hash "
            "tables explained by a Google engineer."
        ),
        "video_url": "https://www.youtube.com/watch?v=RBSGKlAvoiM",
        "cover_url": "https://img.youtube.com/vi/RBSGKlAvoiM/hqdefault.jpg"
    },
    {
        "slug": "machine-learning-for-everybody",
        "title": "Machine Learning for Everybody — Full Course",
        "author": "freeCodeCamp.org",
        "publisher": "YouTube",
        "category": "Technology",
        "description": (
            "An approachable introduction to machine learning concepts and "
            "models, with hands-on Python examples."
        ),
        "video_url": "https://www.youtube.com/watch?v=i_LwzRVP7bg",
        "cover_url": "https://img.youtube.com/vi/i_LwzRVP7bg/hqdefault.jpg"
    },
    {
        "slug": "what-is-a-neural-network",
        "title": "But What Is a Neural Network?",
        "author": "3Blue1Brown",
        "publisher": "YouTube",
        "category": "Technology",
        "description": (
            "A beautifully animated explanation of how neural networks "
            "are structured and how they recognise handwritten digits."
        ),
        "video_url": "https://www.youtube.com/watch?v=aircAruvnKk",
        "cover_url": "https://img.youtube.com/vi/aircAruvnKk/hqdefault.jpg"
    },
    {
        "slug": "crash-course-chemistry",
        "title": "The Nucleus: Crash Course Chemistry #1",
        "author": "CrashCourse",
        "publisher": "YouTube",
        "category": "Science",
        "description": (
            "An energetic first look at atoms, the nucleus, isotopes and "
            "why chemistry shapes the world around us."
        ),
        "video_url": "https://www.youtube.com/watch?v=FSyAehMdpyI",
        "cover_url": "https://img.youtube.com/vi/FSyAehMdpyI/hqdefault.jpg"
    },
    {
        "slug": "crash-course-physics",
        "title": "Motion in a Straight Line: Crash Course Physics #1",
        "author": "CrashCourse",
        "publisher": "YouTube",
        "category": "Science",
        "description": (
            "Position, velocity and acceleration explained clearly as the "
            "starting point for understanding physics."
        ),
        "video_url": "https://www.youtube.com/watch?v=ZM8ECpBuQYE",
        "cover_url": "https://img.youtube.com/vi/ZM8ECpBuQYE/hqdefault.jpg"
    },
    {
        "slug": "crash-course-astronomy",
        "title": "Introduction to Astronomy: Crash Course Astronomy #1",
        "author": "CrashCourse",
        "publisher": "YouTube",
        "category": "Science",
        "description": (
            "Phil Plait introduces the night sky, the scale of the "
            "universe and how astronomers study it."
        ),
        "video_url": "https://www.youtube.com/watch?v=0rHUDWjR5gg",
        "cover_url": "https://img.youtube.com/vi/0rHUDWjR5gg/hqdefault.jpg"
    },
    {
        "slug": "crash-course-world-history",
        "title": "The Agricultural Revolution: Crash Course World History #1",
        "author": "CrashCourse",
        "publisher": "YouTube",
        "category": "History",
        "description": (
            "John Green explores how farming transformed human societies "
            "and set the stage for civilisation."
        ),
        "video_url": "https://www.youtube.com/watch?v=Yocja_N5s1I",
        "cover_url": "https://img.youtube.com/vi/Yocja_N5s1I/hqdefault.jpg"
    },
    {
        "slug": "crash-course-literature",
        "title": "How and Why We Read: Crash Course Literature #1",
        "author": "CrashCourse",
        "publisher": "YouTube",
        "category": "Literature",
        "description": (
            "Why reading matters and how to read critically, as an "
            "introduction to studying great books."
        ),
        "video_url": "https://www.youtube.com/watch?v=MSYw502dJNY",
        "cover_url": "https://img.youtube.com/vi/MSYw502dJNY/hqdefault.jpg"
    },
    {
        "slug": "crash-course-statistics",
        "title": "What Is Statistics: Crash Course Statistics #1",
        "author": "CrashCourse",
        "publisher": "YouTube",
        "category": "Mathematics",
        "description": (
            "An introduction to how statistics helps us describe data, "
            "measure uncertainty and make better decisions."
        ),
        "video_url": "https://www.youtube.com/watch?v=sxQaBpKfDRk",
        "cover_url": "https://img.youtube.com/vi/sxQaBpKfDRk/hqdefault.jpg"
    },
    {
        "slug": "essence-of-linear-algebra",
        "title": "Vectors — Essence of Linear Algebra, Chapter 1",
        "author": "3Blue1Brown",
        "publisher": "YouTube",
        "category": "Mathematics",
        "description": (
            "A visual, intuitive introduction to vectors that opens the "
            "acclaimed Essence of Linear Algebra series."
        ),
        "video_url": "https://www.youtube.com/watch?v=fNk_zzaMoSs",
        "cover_url": "https://img.youtube.com/vi/fNk_zzaMoSs/hqdefault.jpg"
    },
    {
        "slug": "essence-of-calculus",
        "title": "The Essence of Calculus",
        "author": "3Blue1Brown",
        "publisher": "YouTube",
        "category": "Mathematics",
        "description": (
            "Discover the core ideas of calculus through geometry, "
            "starting with the area of a circle."
        ),
        "video_url": "https://www.youtube.com/watch?v=WUvTyaaNkzM",
        "cover_url": "https://img.youtube.com/vi/WUvTyaaNkzM/hqdefault.jpg"
    },
    {
        "slug": "calculus-1-full-course",
        "title": "Calculus 1 — Full College Course",
        "author": "freeCodeCamp.org",
        "publisher": "YouTube",
        "category": "Mathematics",
        "description": (
            "A complete first-semester calculus course: limits, "
            "derivatives, applications and an introduction to integrals."
        ),
        "video_url": "https://www.youtube.com/watch?v=HfACrKJ_Y2w",
        "cover_url": "https://img.youtube.com/vi/HfACrKJ_Y2w/hqdefault.jpg"
    },
    {
        "slug": "big-buck-bunny-clip",
        "title": "Big Buck Bunny — Open Movie Clip",
        "author": "Blender Foundation",
        "publisher": "Blender Foundation",
        "category": "Open Media",
        "description": (
            "A short excerpt from the Blender Foundation's open movie "
            "Big Buck Bunny, released under a Creative Commons licence."
        ),
        "video_url": "videos/big-buck-bunny-clip.mp4",
        "download_url": "https://www.w3schools.com/html/mov_bbb.mp4"
    },
    {
        "slug": "flower-cc0-clip",
        "title": "Flower — CC0 Sample Clip",
        "author": "MDN Contributors",
        "publisher": "Mozilla",
        "category": "Open Media",
        "description": (
            "A short CC0 nature clip from MDN's open media samples, useful "
            "for testing video playback and seeking."
        ),
        "video_url": "videos/flower-cc0-clip.mp4",
        "download_url": (
            "https://interactive-examples.mdn.mozilla.net/"
            "media/cc0-videos/flower.mp4"
        )
    }
]
