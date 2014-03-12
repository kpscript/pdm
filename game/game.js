/*var Q = Quintus()
                .include("Sprites, Scenes, Input, 2D, UI")
                .setup().controls();    */

// HTTP GET Processor from http://www.netlobo.com/url_query_string_javascript.html
function gup( name )
{
    name = name.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]");
    var regexS = "[\\?&]"+name+"=([^&#]*)";
    var regex = new RegExp( regexS );
    var results = regex.exec( window.location.href );
    if( results == null )
        return "";
    else
        return results[1];
}

$.getJSON(gup("stageid") + ".json", function(data) {
    var Q = Quintus()
                    .include("Sprites, Scenes, Input, 2D, UI")
                    .setup({width: data.width*data.spsize, height: data.height*data.spsize})
                    .controls();

    var loader = []
    $.each(data.assets, function(key, value) {
        value = "../".concat(value);
        loader.push(value);
        
        if(key == data.start.ID)
        {
            Q.Sprite.extend("Player", {
                init: function(p) {
                    this._super(p, {asset: value});
                    this.add("2d, platformerControls");
                },
            });
        }
        else if (key == data.end.ID)
        {} // TODO: Add Ending Goal
        else
        {
            Q.Sprite.extend("Block" + key.charCodeAt(0).toString(), {
                init: function(p) {
                    this._super(p, {asset: value})
                },
            });
        }
    });

    Q.load(loader, function() {
        Q.scene("level", function(stage) {
            $.each(data.blocks, function(index, value) {
                var evalstr = "stage.insert(".concat(
                    "new Q.Block", value.ID.charCodeAt(0).toString(), "(",
                        "{x:", (value.x * data.spsize).toString(),
                        ",y:", (value.y * data.spsize).toString(),
                        "}",
                    "));" );
                (new Function('stage', 'Q', evalstr))(stage, Q);
            });
            player = new Q.Player({x:data.start.x*data.spsize, y:data.start.y*data.spsize});
            stage.insert(player);

            // TODO: Insert ending goal (must have added information on it first)
        });

        Q.stageScene("level");
    });
});

/*
Q.Sprite.extend("Block", {
    init: function(p) {
        this._super(p, {asset: "Block.gif",});

        //this.add("2d");
    },
});

Q.Sprite.extend("Player", {
    init: function(p) {
        this._super(p, {asset: "Kirby.gif",});

        this.add("2d, platformerControls");
    },
});

Q.load(["Kirby.gif", "Block.gif",
        ], function() {
    Q.scene("testlevel", function(stage) {
        player = new Q.Player({x:Q.width/2,});
        block = new Q.Block({x:Q.width/2,y:Q.height/2});
        stage.insert(player);
        stage.insert(block);    
    });

    Q.stageScene("testlevel");

});
*/