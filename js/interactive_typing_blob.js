function start_interactive_typing() {
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
		let randomize_order = true;
		let auto_advance = true;
		let any_position = false;
		let drawn_correct_indexes = {};
		if ( typeof window.randomize_order != "undefined" ) { randomize_order = window.randomize_order; }
		if ( typeof window.auto_advance != "undefined" ) { auto_advance = window.auto_advance; }
		if ( typeof window.any_position != "undefined" ) { any_position = window.any_position; }

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
				let font = areas[ i ].getAttribute( "font" );
				if ( font === null ) { font = text_font; }
				rectangle_objects.push({
					area: areas[ i ] ,
					id: id ,
					translated_coordinates: translated_rec_coordinates ,
					font: font
				});
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
				let random_seed = Math.seed( new Date().getTime() );
				let min_seed_iterations = 3;
				let max_seed_iterations = 10;
				let random_number_of_seeds = Math.floor( min_seed_iterations + Math.random() * ( max_seed_iterations + 1 - min_seed_iterations ) );
				for ( let i = 1; i < random_number_of_seeds; ++i ) {
					random_seed = Math.seed( random_seed() );
				}
				Math.random = Math.seed( random_seed() );
				const newArr = array.slice();
				for (let i = newArr.length - 1; i > 0; i--) {
					const rand = Math.floor(Math.random() * (i + 1));
					[newArr[i], newArr[rand]] = [newArr[rand], newArr[i]];
				}
				return newArr
			}

			// https://www.w3schools.com/graphics/canvas_text.asp
			function add_text_to_area( rectangle_object ) {
				// context.font = text_font;
				context.font = rectangle_object.font;
				context.fillStyle = text_color;
				context.textAlign = "center";
				let x = rectangle_object.translated_coordinates[ 0 ] + ( rectangle_object.translated_coordinates[ 2 ] / text_x_offset_factor );
				let y = rectangle_object.translated_coordinates[ 1 ] + ( rectangle_object.translated_coordinates[ 3 ] / text_y_offset_factor );
				context.fillText( rectangle_object.area.alt , x , y );
			}

			// Randomize Items
			if ( randomize_order ) {
				areas = shuffleArray( [ ...areas ] );
				rectangle_objects = shuffleArray( rectangle_objects );
			}

			// Now we just have to highlight boxes/areas in order , and verify typed answer is right before moving on
			let answer_input_element = document.getElementById( "input-answer" );
			let active_rectangle_index = 0;
			let total_rectangles = rectangle_objects.length;
			let time_now = new Date().getTime();
			let time_last_control = new Date().getTime();
			let time_last_control_z = new Date().getTime();
			let control_cooloff = 1.0;
			let control_z_cooloff = 1.0;
			draw_rectangle( ...rectangle_objects[ active_rectangle_index ].translated_coordinates , unanswered_color );
			let hint_button_element = document.getElementById( "hint-button" );
			let hint_area_element = document.getElementById( "hint-area" );
			hint_button_element.addEventListener( "click" , function( event ) {
				hint_area_element.innerText = rectangle_objects[ active_rectangle_index ].area.alt;
				answer_input_element.focus();
				answer_input_element.select();
			});
			answer_input_element.addEventListener( "keyup" , function( event ) {
				let input_text = this.value.toLowerCase();
				if ( active_rectangle_index in drawn_correct_indexes ) {
					console.log( "already answered from anywhere position" );
					while( ( active_rectangle_index in drawn_correct_indexes ) === true ) {
						active_rectangle_index += 1;
						console.log( active_rectangle_index );
					}
				}
				let correct_value = rectangle_objects[ active_rectangle_index ].area.alt.toLowerCase();
				if ( input_text === correct_value ) {
					this.value = "";
					hint_area_element.innerText = "";
					draw_rectangle( ...rectangle_objects[ active_rectangle_index ].translated_coordinates , answered_color );
					add_text_to_area( rectangle_objects[ active_rectangle_index ] );
					drawn_correct_indexes[ active_rectangle_index ] = 1;
					console.log( drawn_correct_indexes );
					active_rectangle_index += 1;
					if ( active_rectangle_index in drawn_correct_indexes ) {
						console.log( "already answered from anywhere position" );
						while( ( active_rectangle_index in drawn_correct_indexes ) === true ) {
							active_rectangle_index += 1;
							console.log( active_rectangle_index );
						}
					}
					if ( active_rectangle_index === total_rectangles ) {
						if ( next_challenge_url ) {
							if ( auto_advance ) {
								window.location.href = next_challenge_url;
							}
						}
					} else {
						draw_rectangle( ...rectangle_objects[ active_rectangle_index ].translated_coordinates , unanswered_color );
					}
				} else {
					//if ( any_position === true ) {
						let potential_correct_values = rectangle_objects.map( ( x ) => { return x.area.alt.toLowerCase() } );
						let pcv = {};
						potential_correct_values.forEach( ( x , i ) => { pcv[ x ] = i } );
						if ( input_text in pcv ) {
							if ( pcv[ input_text ] in drawn_correct_indexes ) { return; }
							console.log( "correct answer for anywhere position" );
							this.value = "";
							hint_area_element.innerText = "";
							active_index = pcv[ input_text ]
							console.log( active_index );
							draw_rectangle( ...rectangle_objects[ active_index ].translated_coordinates , answered_color );
							add_text_to_area( rectangle_objects[ active_index ] );
							drawn_correct_indexes[ active_index ] = 1;
							console.log( drawn_correct_indexes );
							if ( active_index === total_rectangles ) {
								if ( next_challenge_url ) {
									if ( auto_advance ) {
										window.location.href = next_challenge_url;
									}
								}
							}
						}
					//}
				}
			});
			let control_z_listener = false;
			function setup_control_z_listener() {
				answer_input_element.addEventListener( "keydown" , function( event ) {
					if ( event.key !== "Control" ) { return; }
					if ( event.ctrlKey !== true ) { return; }
					time_last_control = new Date().getTime();
					answer_input_element.addEventListener( "keyup" , function( event_two ) {
						if ( event_two.keyCode !== 90 ) { return; } // Control + Z
						time_now = new Date().getTime();
						let time_since_last_control_z = ( ( time_now - time_last_control_z ) / 1000 );
						if ( time_since_last_control_z < control_z_cooloff ) { return; }
						let time_since_last_control = ( ( time_now - time_last_control ) / 1000 );
						if ( time_since_last_control > control_cooloff ) { return; }
						console.log( `Control + Z === ${time_now} === ${time_since_last_control_z}` );
						time_last_control_z = time_now;
						this.value = "";
						hint_area_element.innerText = "";
						draw_rectangle( ...rectangle_objects[ active_rectangle_index ].translated_coordinates , answered_color );
						add_text_to_area( rectangle_objects[ active_rectangle_index ] );
						drawn_correct_indexes[ active_rectangle_index ] = 1;
						console.log( drawn_correct_indexes );
						active_rectangle_index += 1;
						if ( active_rectangle_index in drawn_correct_indexes ) {
							console.log( "already answered from anywhere position" );
							while( ( active_rectangle_index in drawn_correct_indexes ) === true ) {
								active_rectangle_index += 1;
								console.log( active_rectangle_index );
							}
						}
						if ( active_rectangle_index === total_rectangles ) {
							if ( next_challenge_url ) {
								if ( auto_advance ) {
									//window.location.href = next_challenge_url;
								}
							}
						} else {
							draw_rectangle( ...rectangle_objects[ active_rectangle_index ].translated_coordinates , unanswered_color );
						}
						return;
					});
				});
			}
			setup_control_z_listener();

			answer_input_element.addEventListener( "keydown" , function( event ) {
				// console.log( "here" );
				// console.log( event.ctrlKey , event.key , event.keyCode );
				if ( event.key === "Control" && event.keyCode === 17 ) {
					// console.log( "there" );
					hint_area_element.innerText = rectangle_objects[ active_rectangle_index ].area.alt;
					answer_input_element.focus();
					answer_input_element.select();
				}
			});
			answer_input_element.focus();
			answer_input_element.setSelectionRange( answer_input_element.value.length , answer_input_element.value.length , "forward" );
		}
		if ( next_challenge_url ) {
			let hint_button = document.getElementById( "hint-button" );
			let next_button_html = `&nbsp;<button class="btn btn-outline-secondary" type="button" id="next-button">Next</button>`;
			hint_button.insertAdjacentHTML( "afterend" , next_button_html );
			document.getElementById( "next-button" ).addEventListener( "click" , function () {
				window.location.href = next_challenge_url;
			});
		}
	}
	init();
}