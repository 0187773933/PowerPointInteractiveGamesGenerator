function start_interactive_drag_and_drop() {
	// window.addEventListener( "scroll" , function() {
	// 	window.scrollTo( 0 , 0 );
	// });

	// https://stackoverflow.com/questions/3971841/how-to-resize-images-proportionally-keeping-the-aspect-ratio
	// https://stackoverflow.com/questions/15192343/drawimage-and-resize-to-canvas#15193645
	// https://stackoverflow.com/questions/5014851/get-click-event-of-each-rectangle-inside-canvas
	// http://jsfiddle.net/BmeKr/1291/
	// https://eli.thegreenplace.net/2010/02/13/finding-out-the-mouse-click-position-on-a-canvas-with-javascript/
	// https://www.w3schools.com/tags/att_area_coords.asp
	function init() {

		let image_source_url = window.image_source_url;
		let image_scale_percentage = window.image_scale_percentage;
		let unanswered_color = window.unanswered_color;
		let answered_color = window.answered_color;
		let text_color = window.text_color;
		let text_font = window.text_font;
		let text_x_offset_factor = window.text_x_offset_factor;
		let text_y_offset_factor = window.text_y_offset_factor;
		let next_challenge_url = window.next_challenge_url;


		let width_scale_percentage = ( image_scale_percentage / 100 );
		let height_scale_percentage = ( image_scale_percentage / 100 );

		let canvas = document.getElementById( "interactive-image-canvas" );
		let context = canvas.getContext( "2d" );
		let image = new Image();
		let scaled_x = 0;
		let scaled_y = 0;
		image.addEventListener( "load" , function() {
			// idk man
			// https://stackoverflow.com/questions/19262141/resize-image-with-javascript-canvas-smoothly#19262385
			scaled_x = ( image.width * width_scale_percentage );
			scaled_y = ( image.height * height_scale_percentage );
			canvas.width = scaled_x;
			canvas.height = scaled_y;
			context.drawImage( image , 0 , 0 , scaled_x , scaled_y );
			add_areas();
		});
		// https://www.image-map.net/
		image.src = image_source_url;

		function draw_line( x1 , y1 , x2 , y2 ) {
			context.beginPath();
			context.moveTo( x1 , y1 );
			context.lineTo( x2 , y2 );
			context.strokeStyle = "#ff0000";
			context.lineWidth = 1;
			context.stroke();
		}

		function draw_rectangle( x1 , y1 , x2 , y2 , hex_color="#ff0000" ) {
			context.beginPath();
			context.rect( x1 , y1 , x2 , y2 )
			context.strokeStyle = hex_color;
			context.lineWidth = 3;
			context.stroke();
		}
		function translate_raw_rectangle_coordinates_to_ordered( raw_input_coordinates ) {
			let input = raw_input_coordinates.split( "," ).map( x => parseInt( x ) );
			input[ 0 ] = Math.round( ( input[ 0 ] * width_scale_percentage ) );
			input[ 1 ] = Math.round( ( input[ 1 ] * height_scale_percentage ) );
			input[ 2 ] = Math.round( ( input[ 2 ] * width_scale_percentage ) );
			input[ 3 ] = Math.round( ( input[ 3 ] * height_scale_percentage ) );
			let ordered;
			if ( input[ 0 ] > input[ 2 ] ) {
				ordered = [ input[ 2 ] , input[ 3 ] , input[ 0 ] , input[ 1 ] ];
			}
			else {
				ordered = input;
			}
			let x_size = ( ordered[ 2 ] - ordered[ 0 ] );
			let y_size = ( ordered[ 3 ] - ordered[ 1 ] );
			// let y_size = Math.abs( ordered[ 3 ] - ordered[ 1 ] );
			let final = [ ordered[ 0 ] , ordered[ 1 ] , x_size , y_size ];
			return final;
		}
		function draw_circle_at_point( x , y , hex_color="#ff0000" ) {
			context.beginPath();
			context.arc( x , y , 3 , 0 , ( 2 * Math.PI ) );
			context.strokeStyle = hex_color;
			context.lineWidth = 1;
			context.stroke();
		}
		// https://stackoverflow.com/questions/16628184/add-onclick-and-onmouseover-to-canvas-element
		function is_point_inside_rectangle( mouse_x , mouse_y , rec_coords ) {
			let x1 = rec_coords[ 0 ];
			let y1 = rec_coords[ 1 ];
			let x2 = rec_coords[ 2 ];
			let y2 = rec_coords[ 3 ];
			let bottom_left = { x: x1 , y: y1 };
			let bottom_right = { x: ( x1 + x2 ) , y: y1 };
			let top_left = { x: x1 , y: ( y1 + y2 ) };
			let top_right = { x: ( x1 + x2 ) , y: ( y1 + y2 ) };
			// draw_circle_at_point( bottom_left.x , bottom_left.y );
			// draw_circle_at_point( bottom_right.x , bottom_right.y );
			// draw_circle_at_point( top_left.x , top_left.y );
			// draw_circle_at_point( top_right.x , top_right.y );

			// console.log( `1.) x === ${mouse_x} > ${bottom_left.x}` );
			if ( mouse_x > bottom_left.x ) {
				// console.log( `2.) x === ${mouse_x} < ${bottom_right.x}` );
				if ( mouse_x < bottom_right.x ) {
					// console.log( `3.) y === ${mouse_y} > ${top_left.y}` );
					if ( mouse_y > top_left.y ) {
						// console.log( `4.) y === ${mouse_y} < ${bottom_right.y}` );
						if ( mouse_y < bottom_right.y ) {
							return true;
						}
					}
				}
			}
			return false;
		}
		function add_areas() {
			// Cross
			// draw_line( 0 , 0 , scaled_x , scaled_y ); // top left corner to bottom right corner
			// draw_line( 0 , scaled_y , scaled_x , 0 ); // bottom left corner to top right corner

			// Middle
			let midpoint_x = ( scaled_x / 2 );
			let midpoint_y = ( scaled_y / 2 );
			// draw_line( midpoint_x , 0 , midpoint_x , scaled_y ); // vertical across
			// draw_line( 0 , midpoint_y , scaled_x , midpoint_y ); // horizontal across

			// Setup Area Rectangles
			let areas = document.querySelectorAll( "area" );
			let rectangle_objects = [];
			for ( let i = 0; i < areas.length; ++i ) {
				let translated_rec_coordinates = translate_raw_rectangle_coordinates_to_ordered( areas[ i ].getAttribute( "coords" ) );
				let id = areas[ i ].alt.toLowerCase().replace( /\s+/g , '-' );
				rectangle_objects.push({
					area: areas[ i ] ,
					id: id ,
					translated_coordinates: translated_rec_coordinates
				})
				// draw_rectangle( ...translated_rec_coordinates );
			}
			// console.log( rectangle_objects );
			// console.log( canvas );
			canvas.addEventListener( "click" , function( event ) {
				let mouse_translated_x = ( event.clientX - canvas.offsetLeft );
				let mouse_translated_y = ( event.clientY - canvas.offsetTop );
				// draw_circle_at_point( mouse_translated_x , mouse_translated_y );
				for ( let i = 0; i < rectangle_objects.length; ++i ) {
					let inside_rectangle = is_point_inside_rectangle( mouse_translated_x , mouse_translated_y , rectangle_objects[ i ].translated_coordinates );
					if ( inside_rectangle ) {
						console.log( `we clicked inside object ${rectangle_objects[ i ].area.alt}` , rectangle_objects[ i ] );
						return;
					}
				}
			});

			// https://stackoverflow.com/a/46161940
			function shuffleArray(array) {
				// https://stackoverflow.com/a/23304189
				Math.seed = function(s) {
					return function() {
						s = Math.sin(s) * 10000; return s - Math.floor(s);
					};
				};
				let random1 = Math.seed(new Date().getTime());
				let random2 = Math.seed(random1());
				Math.random = Math.seed(random2());
				const newArr = array.slice();
				for (let i = newArr.length - 1; i > 0; i--) {
					const rand = Math.floor(Math.random() * (i + 1));
					[newArr[i], newArr[rand]] = [newArr[rand], newArr[i]];
				}
				return newArr
			}

			// https://www.w3schools.com/graphics/canvas_text.asp
			function add_text_to_area( rectangle_object ) {
				context.font = text_font;
				context.fillStyle = text_color;
				context.textAlign = "center";
				let x = rectangle_object.translated_coordinates[ 0 ] + ( rectangle_object.translated_coordinates[ 2 ] / text_x_offset_factor );
				let y = rectangle_object.translated_coordinates[ 1 ] + ( rectangle_object.translated_coordinates[ 3 ] / text_y_offset_factor );
				context.fillText( rectangle_object.area.alt , x , y );
			}

			// Dynamically Create Draggable Text Boxes
			let label_container = document.getElementById( "draggable-label-container" );
			areas = shuffleArray( [ ...areas ] );
			for ( let i = 0; i < areas.length; ++i ) {
				let id = areas[ i ].alt.toLowerCase().replace( /\s+/g , '-' );
				let text_box_label = `<p class="text-box-label draggable" id="${id}">${areas[ i ].alt}</p>`;
				label_container.insertAdjacentHTML( "beforebegin" , text_box_label );
			}

			let active_rectangle_index = 0;
			let total_rectangles = rectangle_objects.length;
			$( ".draggable" ).draggable({
				// https://api.jqueryui.com/draggable/#event-stop
				stop: function( event , ui ) {
					let mouse_translated_x = ( event.clientX - canvas.offsetLeft );
					let mouse_translated_y = ( event.clientY - canvas.offsetTop );
					for ( let i = 0; i < rectangle_objects.length; ++i ) {
						let inside_rectangle = is_point_inside_rectangle( mouse_translated_x , mouse_translated_y , rectangle_objects[ i ].translated_coordinates );
						if ( inside_rectangle ) {
							// console.log( `we dropped something inside object ${rectangle_objects[ i ].area.alt}` , rectangle_objects[ i ] );
							if ( rectangle_objects[ i ].id === ui.helper[ 0 ].id ) {
								console.log( `we dropped ${ui.helper[ 0 ].id} inside CORRECT location of ${rectangle_objects[ i ].id}` );
								draw_rectangle( ...rectangle_objects[ i ].translated_coordinates , answered_color );
								active_rectangle_index += 1;
								if ( active_rectangle_index === total_rectangles ) {
									if ( next_challenge_url ) {
										window.location.href = next_challenge_url;
									}
								}
							}
							else {
								// console.log( `we dropped ${ui.helper[ 0 ].id} inside INCORRECT location of ${rectangle_objects[ i ].id}` );
							}
							return;
						}
					}
				}
			});

		}

	}
	init();
}