<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>4 Grid App</title>

<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        height: 100vh;
        overflow: hidden; /* No Scroll */
        font-family: Arial, sans-serif;
    }

    .container {
        display: grid;
        grid-template-columns: 1fr 1fr;   /* 2 columns */
        grid-template-rows: 1fr 1fr;      /* 2 rows */
        height: 100vh;                    /* Full screen */
        width: 100vw;
    }

    .box {
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 22px;
        font-weight: bold;
        color: white;
    }

    .box1 { background: #ff6b6b; }
    .box2 { background: #4ecdc4; }
    .box3 { background: #1a535c; }
    .box4 { background: #ffa600; }
</style>

</head>

<body>

<div class="container">
    <div class="box box1">Grid 1</div>
    <div class="box box2">Grid 2</div>
    <div class="box box3">Grid 3</div>
    <div class="box box4">Grid 4</div>
</div>

</body>
</html>
