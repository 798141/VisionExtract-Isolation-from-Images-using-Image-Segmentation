<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>VisionExtract – Subject Isolation</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            /* Baby pink + whitish gradient */
            background: linear-gradient(135deg, #f4c2c2 0%, #ffeef2 50%, #ffffff 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .container {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 16px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
            padding: 24px 32px;
            max-width: 900px;
            width: 90%;
        }

        h1 {
            text-align: center;
            margin-top: 0;
            color: #b3547a;
            letter-spacing: 0.03em;
        }

        p.subtitle {
            text-align: center;
            color: #7a4661;
            margin-bottom: 20px;
        }

        .upload-box {
            border: 2px dashed #f4c2c2;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            background-color: #fff7fa;
            cursor: pointer;
        }

        .upload-box:hover {
            background-color: #ffe9f2;
        }

        input[type="file"] {
            display: none;
        }

        .btn-submit {
            margin-top: 16px;
            background-color: #ffb6c1;
            border: none;
            color: #5b2f41;
            padding: 10px 20px;
            border-radius: 20px;
            cursor: pointer;
            font-weight: 600;
        }

        .btn-submit:hover {
            background-color: #ff9fb0;
        }

        .preview-wrapper {
            display: flex;
            justify-content: space-between;
            gap: 20px;
            margin-top: 24px;
            flex-wrap: wrap;
        }

        .preview-card {
            flex: 1 1 45%;
            background: #fff;
            border-radius: 12px;
            padding: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
            text-align: center;
        }

        .preview-card h3 {
            margin-top: 0;
            color: #b3547a;
            font-size: 1rem;
        }

        .preview-card img {
            max-width: 100%;
            max-height: 300px;
            border-radius: 8px;
            object-fit: contain;
        }

        .helper-text {
            font-size: 0.85rem;
            color: #8a5973;
        }
    </style>
</head>
<body>
<div class="container">
    <h1>VisionExtract</h1>
    <p class="subtitle">Upload an image to isolate the main subject using image segmentation.</p>

    <form method="POST" enctype="multipart/form-data">
        <label for="imageInput" class="upload-box">
            <strong>Click to select an image</strong><br>
            <span class="helper-text">Supported formats: JPG, JPEG, PNG</span><br><br>
            <span id="fileName" class="helper-text">No file chosen</span>
        </label>
        <input id="imageInput" type="file" name="image" accept="image/*" onchange="showFileName(event)">

        <div style="text-align:center;">
            <button type="submit" class="btn-submit">Run VisionExtract</button>
        </div>
    </form>

    <div class="preview-wrapper">
        <div class="preview-card">
            <h3>Input Image</h3>
            {% if input_image %}
                <img src="{{ input_image }}" alt="Input image">
            {% else %}
                <p class="helper-text">Upload an image to see it here.</p>
            {% endif %}
        </div>

        <div class="preview-card">
            <h3>Isolated Subject</h3>
            {% if result_image %}
                <img src="{{ result_image }}" alt="Segmented output">
            {% else %}
                <p class="helper-text">Result will appear here after processing.</p>
            {% endif %}
        </div>
    </div>
</div>

<script>
    function showFileName(event) {
        const input = event.target;
        const fileNameSpan = document.getElementById("fileName");
        if (input.files && input.files[0]) {
            fileNameSpan.textContent = input.files[0].name;
        } else {
            fileNameSpan.textContent = "No file chosen";
        }
    }
</script>
</body>
</html>
