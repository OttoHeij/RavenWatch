var jdata;

var cam_images = [];


/* Call back when we want to update. This is the preloader for smooth image loading. */
$.fn.preload = function () {

    for (i = 0; i < this.length; i++)
    {
        $(".cam-" + i).attr("src", this[i]);
    }

    //console.log(this[0]);

}



function do_cams()
{

    var img_width = (100).toString()  + "%";

    if (jdata.stream_count > 1)
    {
        img_width = (50).toString()  + "%";
    }


    /* Lets create our img tag dynamically. cam-1, cam-2 etc. Only do this once! */
    if (cam_images.length == 0)
    {
        //alert("adding image")
        for (i = 0; i < jdata.stream_count; i++)
        {
            var image = new Image();
            
            cam_images.push(image);

            var img = document.createElement("img");
            img.setAttribute('class', 'cam-' + i);
            img.setAttribute('style', 'width:' + img_width + ';border:1px solid red;');       
            $(".cams").append(img);

        }
    }

    var imgs = [];

    for (i = 0; i < jdata.stream_count; i++)
    {
        d = new Date();

        t = "/frame/" + i.toString() + "/" + d.getTime();
    
        imgs[i] = t;

    }

    $(imgs).preload();

    
}


function update_screen()
{
    $(".stream_count").text(jdata.stream_count);
    $(".uptime").text(jdata.streams[0].uptime);
    do_cams();
}


function poll_data()
{
    ts = Math.round((new Date()).getTime() / 1000);
    $.get("/json", {  },  function(data,status){ jdata = JSON.parse(data); });
    update_screen();
}


function start_ui()
{
       
    $(function() {
        setInterval(poll_data, 1000);
    
      });
      
}
