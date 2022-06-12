document.getElementById('formFile').addEventListener("change", function () {
    document.getElementById('input_image').src = URL.createObjectURL(this.files[0]);
});

document.getElementById('cloning_button').addEventListener('click', function () {
    this.disabled = true;
    document.getElementById('cloning_spinner').classList.remove('d-none');
    // upload blob image url to server
    let form = new FormData(document.getElementById('cloning_options'));
    let blob_url = document.getElementById('input_image').src;
    // get the image from object url and send to server
    axios.get(blob_url, { responseType: 'blob' }).then(response => {
        return new File([response.data], 'inputImage')
    }).then(file => {
        form.append('image', file);
        axios.post('/api/cloning', form).then(function (response) {
            console.log('Upload Success');
            document.getElementById('result_image').src = response.data.result;
            // document.getElementById('text-tab').disabled = false;
        }).catch(function (error) {
            alert('Upload Failed');
        }).finally(() => {
            this.disabled = false;
            document.getElementById('cloning_spinner').classList.add('d-none');
        });
    })
})