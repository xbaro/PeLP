var j=jQuery.noConflict();

j(document).ready(function(){

	/* Expand Collapse Rows Funcionality */
	var tSpeed = 300;							// transition speed
												// (milliseconds)
	var tEffect = 'easeInOutExpo';				// transition effect
	var orow = null;							// link row opened (for
												// accordeon rows)

	jQuery.fn.expandCollapseRow = function (id) {
		var elm = j("#" + id);
		var tr = j(this).parent().parent();
		var acc = j(this).data('accordeon');

		if (j(this).hasClass('collapsed')) {
			j(this).removeClass('collapsed').addClass('expanded');
			tr.addClass('expanded');
			tr.find('.tmp').css({opacity: 1}).animate({opacity: 0}, tSpeed);
			
			if(acc){
				if(orow!=null && orow!=j(this)){
					var otr = orow.parent().parent();
					var ocont = j("#"+orow.attr('rel'));
					orow.removeClass('expanded').addClass('collapsed');
					otr.find('.tmp').css({opacity: 0}).animate({opacity: 1}, tSpeed);
					otr.removeClass('expanded');
					ocont.slideToggle(tSpeed, tEffect);
				}
				orow=j(this);
			}

		}else{
			j(this).removeClass('expanded').addClass('collapsed');
			tr.removeClass('expanded');
			tr.find('.tmp').css({opacity: 0}).animate({opacity: 1}, tSpeed);
			if(acc) orow=null;
		}
			
		elm.slideToggle(tSpeed, tEffect);
	};

	/* Common */

	// IE6 first-child & last-child pseudo-selectors hack
	if ( j.browser.msie && j.browser.version=='6.0') {
		j('tr td:first-child').addClass('first-child');
		j('tr th:first-child').addClass('first-child');
		j('tr:first-child').addClass('first-child');
		j('tr:last-child').addClass('last-child');
	}

	// Mac hacks
	if(navigator.userAgent.indexOf('Mac') > 0)
    	j('body').addClass('mac-os');

	// Eventos de filtros s_activ
//	j('#s_assign').attr('disabled',true);
//	j('#s_aula').attr('disabled',true);
//	j('#s_activ').attr('disabled',true);

    // Ocultar elementos iniciales
	j('#send_filters').hide();
	
	// Miramos si estan selecionados los combos en caso de estar no los ponemos ocultos
	
	
	if(j('.profile').html()!= null){
		j("#s_assign").attr('disabled',false);
		j('#delviMENUn').show();
	}else
		j('#delviMENUn').hide();
	
	if(j("#s_assign option:selected").val()!=""&&j("#s_assign option:selected").val()!="-1")j("#s_assign").attr('disabled',false);
	if(j("#s_activ option:selected").val()!=""&&j("#s_activ option:selected").val()!="-1")j("#s_activ").attr('disabled',false);
	if(j("#s_aula option:selected").val()!=""&&j("#s_aula option:selected").val()!="-1")j("#s_aula").attr('disabled',false);
	
	

    /* Envíos */

	// Establecer placeholders para navegadores no compatibles
	j('input[placeholder]').placeholder();

	// Customizar elementos de formulario
	j('input').customFormInput({
		browseLbl: 'Examinar...',				/* browse button label */
		changeLbl: 'Canviar...',				/* change button label */
		noneLbl: 'Cap fitxer seleccionat'		/* no file label */
	});

	// Control In/Out
	j("a.commut").click(function(ev) {
		ev.preventDefault();
		var id = j(this).attr('id');
		if( j(this).hasClass('text') ){
			j(this).addClass('file').html('Introduir com a text').removeClass('text');
			j('div.'+id+'_text').hide();
			j('div.'+id+'_file').show();
		}else{
			j(this).addClass('text').html('Adjuntar com arxiu').removeClass('file');
			j('div.'+id+'_file').hide();
			j('div.'+id+'_text').show();
		}
	});

	// Iniciar pestañas
	j(".tab_content").hide();
	j("ul.tabs li:first").addClass("active").show();
	j(".tab_content:first").show();
	
	// Control pestañas
	j("ul.tabs li a").click(function(ev) {
		ev.preventDefault();
		j("ul.tabs li").removeClass("active");
		j(this).parent().addClass("active");
		j(".tab_content").hide();
		var activeTab = j(this).attr("href");
		j(activeTab).show();
	});
	
	// pesta�as de navegaci�n general
	j(".tab_content_menu").hide();
	// Cargamos dependiendo de valor call
	if(j("#ajaxCall").val()=="true"){
		j("ul.menu li:first").addClass("active").show();
		j(".tab_content_menu:first").show();
	}else{
		j("ul.menu li:last").addClass("active").show();
		j(".tab_content_menu:last").show();	
	}
			// Control pestañas
	j("ul.menu li a").click(function(ev) {
		ev.preventDefault();
		j("ul.menu li").removeClass("active");
		j(this).parent().addClass("active");
		j(".tab_content_menu").hide();
		var activeTab = j(this).attr("href");
		j(activeTab).show();
	});

	// Selección multiple checkbox
	j('#chk_all').click(function(ev) {
        j("input[name='chk_del'][type='checkbox']").attr('checked', j(this).is(':checked')).trigger('updateState');
    });

    // Borrar archivos seleccionados
    j('#lnk_del').click(function(ev) {
    	// comprovamos si tiene eleguido los combos.
    	s_assign = j("#s_assign").val();
    	s_aula = j("#s_aula").val();
    	s_activ = j("#s_activ").val();
    	petitionClassroom = "";
    	
    	if(s_assign)petitionClassroom += "&s_assign="+s_assign;
    	if(s_aula)petitionClassroom += "&s_aula="+s_aula;
    	if(s_activ)petitionClassroom += "&s_activ="+s_activ;
    	j("input[name='chk_del'][type='checkbox']").each(function(i){
    		if(j(this).is(':checked')){
    			callback="";
    			j.ajax({
    				  url: "deliveries!delete.html",
    				  dataType: 'json',
    				  data: "auxInfo="+j('#chk_del_title_hash'+j(this).val()).val()+"&timeFile="+j("#deliveries_timeFile").val()+petitionClassroom,
    				  error: function(data) {
    			        	if(data.responseText){
    			        		init = data.responseText.indexOf("Exception:")+10;
    			        		fin = data.responseText.substr(init,data.responseText.indexOf("edu.")).indexOf("\n");
    			        		stringFinal = data.responseText.substr(init,fin);
    			        		new Messi("Error: "+stringFinal); j('body').removeClass("loading");
    			        	}else{
    			        		new Messi("Error");
    			        	}
    			        },
    				  success: callback,
    				  type: "POST"
    				});
    			j('#frow_'+j(this).val()).remove();
    		}
    	});
    });
    
    
    // cargar dinamicamente los combo.
    j('#s_assign').change(function(ev){
    	j("#deliveries_s_assign").val(j(this).val());
    	j('#s_aula').val("-1");
    	j('#s_activ').val("-1");
    	callback="";
    	j('body').addClass("loading"); 
    	j.ajax({
			  url: "home!combo.html",
			  dataType: 'json',
			  data: "s_assign="+j(this).val(),
			  error: function(data) {
		        	if(data.responseText){
		        		init = data.responseText.indexOf("Exception:")+10;
		        		fin = data.responseText.substr(init,data.responseText.indexOf("edu.")).indexOf("\n");
		        		stringFinal = data.responseText.substr(init,fin);
		        		new Messi("Error: "+stringFinal); j('body').removeClass("loading");
		        	}else{
		        		new Messi("Error");
		        	}
		        },
			  success:function(data){
				
				var options = "";
				classrooms = data.listClassroms
				for (var i = 0; i < classrooms.length; i++) {
					options += '<option value="' + classrooms[i].index + '">' +j('.textAula').html() +" "+ classrooms[i].index + '</option>';
				}
				j('#s_aula').html(options);
				j('#s_aula').attr('disabled',false);
				if(classrooms.length == 1){
						j.ajax({
							  url: "home!combo.html",
							  dataType: 'json',
							  data: "s_assign="+j("#s_assign").val()+"&s_aula="+classrooms[0].index,
							  error: function(data) {
						        	if(data.responseText){
						        		init = data.responseText.indexOf("Exception:")+10;
						        		fin = data.responseText.substr(init,data.responseText.indexOf("edu.")).indexOf("\n");
						        		stringFinal = data.responseText.substr(init,fin);
						        		new Messi("Error: "+stringFinal); j('body').removeClass("loading");
						        	}else{
						        		new Messi("Error");
						        	}
						        },
							  success:function(data2){
								  
								  var options = "";
								  
								classrooms2 = data2.listActivity
								total = classrooms2.length;
								for (var a = 0; a < classrooms2.length; a++) {
									if(a<total){
										if(classrooms2[a] !== "undefined"){
											options += '<option value="' + classrooms2[a].index + '">' + classrooms2[a].description + '</option>';	
										}
									}
								}
								j('#s_activ').html(options);
								j('#s_activ').attr('disabled',false);
								if(classrooms2.length == 1){
									j("#deliveries_s_activ").val(classrooms2[0].index);
									j('#form_filters').submit();
								}else{
									j('#s_activ').html(options);
									j('#tAlumno').html("");
									
								}
								j('body').removeClass("loading"); 
							  },
							  type: "POST"
							});
				}else{
					j('#s_aula').html(options);
					j('#tAlumno').html("");
				}
				j('body').removeClass("loading"); 
			  },
			  type: "POST"
			});
    	
    });
    
    j('#s_aula').change(function(ev){
    	
    	j("#deliveries_s_aula").val(j(this).val());
    	j('#s_activ').val("-1");
    	callback="";
    	j('body').addClass("loading"); 
    	j.ajax({
			  url: "home!combo.html",
			  dataType: 'json',
			  data: "s_assign="+j("#s_assign").val()+"&s_aula="+j(this).val(),
			  error: function(data) {
		        	if(data.responseText){
		        		init = data.responseText.indexOf("Exception:")+10;
		        		fin = data.responseText.substr(init,data.responseText.indexOf("edu.")).indexOf("\n");
		        		stringFinal = data.responseText.substr(init,fin);
		        		new Messi("Error: "+stringFinal); j('body').removeClass("loading");
		        	}else{
		        		new Messi("Error");
		        	}
		        },
			  success:function(data){
				var options = j("#s_activ option")[0].outerHTML
				classrooms = data.listActivity
				for (var i = 0; i < classrooms.length; i++) {
					options += '<option value="' + classrooms[i].index + '">' + classrooms[i].description + '</option>';
				}
				j('#s_activ').html(options);
				j('body').removeClass("loading"); 
			  },
			  type: "POST"
			});
    	
    	j('#s_activ').attr('disabled',false);
    });
    
    j('#s_activ').change(function(ev){
    	j("#deliveries_s_activ").val(j(this).val());
    	this.form.submit();
    });
    
    j("#progMENUn").click(function(ev) {
    	j("#ajaxCall").val(true);
    });
    
    j("#delviMENUn").click(function(ev) {
    	j("#ajaxCall").val(false);
    });

    /* Entregas */

	j('.tablesorter').tablesorter({
		sortList: [[0,0]],
		selectorHeaders: 'thead.thead th',
		headers: { 
			4: { sorter: false }, 
            5: { sorter: false } 
        },
		textExtraction: function(node) { 
            return j(node).find('span.lbl').html(); 
        },
        debug: false
	});

	j('#tProfesor > tbody > tr > td > a').each(function(){
		j(this).data('accordeon', true);
	});

	j('a.toggle').prepend('<span class="icon"></span>');
	j('a.toggle').click(function(ev) {
		ev.preventDefault();
		j(this).expandCollapseRow(j(this).attr('rel'));
	});


	j('a.collapsed').each(function(){
		j("#" + j(this).attr('rel')).hide();
	});

	j('a.expanded').each(function(){
		var tr = j(this).parent().parent();
		tr.addClass('expanded');
	});

	/* Test Info */

	j('.accordion h3:first').addClass('active');
	j('.accordion .acontent:not(:first)').hide();
	j('.accordion h3').prepend('<span class="icon"></span>').click(function(){
		j(this).next('.acontent').slideToggle(tSpeed, tEffect).siblings(".acontent:visible").slideUp(tSpeed, tEffect);
		j(this).toggleClass('active');
		j(this).siblings('h3').removeClass('active');
	});
	
	/* ajax calls */
	
	j('.ajax-tab').each(function(ind, elem){
		var thisTab = j(this);
		thisTab.click(function(event){
			var href = thisTab.attr('href');
			var whichTab = jQuery.deparam( href )['?activeTab'];
			var modifiedHref = jQuery.param.querystring( href, 'ajaxCall=true' );
			jQuery.ajax({
				url: modifiedHref,
				beforeSend: doBeforeChangeTab,
				success: function(data, textStatus, jqXHR){
					doChangeTab(data, textStatus, jqXHR, whichTab);
				},
				error: doErrorChangingTab,
				complete: doCompleteChangeTab
			});
			event.preventDefault();
		});
	});
	
	
	j('#deliveries_formCall').val(true);
	j('#deliveries').ajaxForm({
        beforeSubmit: function() {
        	// Comprovamos si no pasa el numeor maximo de entregas.
        	
        	if(j(':file').val()!=""){
	        	if(!validate_filename((j(':file').val()))){
	        		new Messi(j(".koFile").html());
	        		return false;
	        	}
        	}        	
        	
        	
        	if(j('#deliveries_totalDelivers').val()>j('#deliveries_maxDelivers')&&j('#chk_entrega').val()!="undefined"){
        		new Messi(j(".koLimit").html());
        		return false;
        	}
        	
        	j('#messagesFINAL').html('<p></p>');
        	j('body').addClass("loading"); 
        },
        error: function(data) {
        	if(data.responseText){
        		init = data.responseText.indexOf("Exception:")+10;
        		fin = data.responseText.substr(init,data.responseText.indexOf("edu.")).indexOf("\n");
        		stringFinal = data.responseText.substr(init,fin);
        		new Messi("Error: "+stringFinal); j('body').removeClass("loading");
        	}else{
        		new Messi("Error");
        	}
        },
        success: function(data) {
        	// Miramos si el resultado es de message o de fileupload.
            if(data.resulMessage){
            	j('#deliveries_timeFile').val(data.timeFile); // el fichero que se usa.
            	j('#messagesFINAL').html('<p>'+data.resulMessage+'</p>');
            	j('body').removeClass("loading");
            	
            	
            	if(data.resulMessage=="OK" && data.finalDeliver){
            		s_assign = j("#s_assign").val();
                	s_aula = j("#s_aula").val();
                	s_activ = j("#s_activ").val();
                	petitionClassroom = "";
                	
                	if(s_assign)petitionClassroom += "&s_assign="+s_assign;
                	if(s_aula)petitionClassroom += "&s_aula="+s_aula;
                	if(s_activ)petitionClassroom += "&s_activ="+s_activ;
                	
            		j(window).attr("location","home.html?ajaxCall=false"+petitionClassroom);
            	}else if(data.resulMessage=="OK"){
            		//new Messi(j(".okCompile").html());
            	}
            	
            }else{
            	if(data.matrizFile){
	            	var out = j('#fileuploadajax'); // Creamos el listado de ficheros.
	            	content = "";
	            	j.each(data.matrizFile, function(index, value) {
	            		
	            		content += "<tr id='frow_"+index+"'><td>";
	            		content += "<input type='checkbox' name='chk_del' id='chk_del_"+index+"' value='"+index+"' />";
	            		content += "<label id='"+index+"'  for='chk_del_"+index+"'>"+value[0]+"</label>";
	            		content += "<input type='hidden' id='chk_del_title_hash"+index+"'  value='"+value[4]+"'/>";
	            		content += "</td><td class='opt'>";
	            		content += "<input type='checkbox' name='matrizFile' value='c"+value[4]+"' id='chk_code_"+index+"'/><label for='chk_code_"+index+"'><span class='hidden'>"+j("code").html()+"</span></label></td>";
	            		content += "<td class='opt'><input type='checkbox' name='matrizFile' value='m"+value[4]+"' id='chk_memo_"+index+"'/><label for='chk_memo_"+index+"'><span class='hidden'>"+j("memori").html()+"</span></label></td>";
	            		content += "<td class='opt'><input type='checkbox' name='matrizFile' value='f"+value[4]+"' id='chk_file_"+index+"'/><label for='chk_file_"+index+"'><span class='hidden'>"+j("principal").html()+"</span></label></td>";
	            		content += "</tr>";
	            	});
	            	out.html(content);
	            	// eliminamos los cambos anteriores
	            	j(".customfile").html("<input id='deliveries_upload' class='customfile-input' type='file' value='' name='upload'>")
	            	j('#deliveries_timeFile').val(data.timeFile); // el fichero que se usa.
	            	j('input').customFormInput({
	            		browseLbl: 'Examinar...',				/* browse button label */
	            		changeLbl: 'Canviar...',				/* change button label */
	            		noneLbl: 'Cap fitxer seleccionat'		/* no file label */
	            	});
            	}else{
            		new Messi(j(".needFile").html());
            	}
            	j('body').removeClass("loading"); 
            }
        }
    });



/* Llamar ajax para cargar delivers*/

j(".toggle").click(function(ev) {
	if(j(this).attr("id")=="ajaxDelivers"){
		userId=j(this).attr("href").substr(1,(j(this).attr("href").length));
		
		
		if(j(this).attr("class")=="toggle expanded"){
			j.ajax({
			  url: "home!detaill.html",
			  dataType: 'json',
			  data: "s_assign="+j("#s_assign").val()+"&userId="+userId+"&s_activ="+j("#s_activ").val(),
			  error: function(data) {
	    		init = data.responseText.indexOf("Exception:")+10;
	    		fin = data.responseText.substr(init,data.responseText.indexOf("edu.")).indexOf("\n");
	    		stringFinal = data.responseText.substr(init,fin);
	    		new Messi("Error: "+stringFinal); j('body').removeClass("loading");
		        },
			  success:function(data){
				  
				  resultDelivers = "<table class=\"tlevel_2\"><tbody>";
				  
				  j.each(data.listDeliverDetails, function(index, value) {
					  if(value!=null){
						  resultDelivers += "<tr>";
						  resultDelivers += "<td><a href=\"#\" class=\"toggle collapsed\" rel=\"a"+userId+"_e"+index+"\"><span class=\"lbl\">"+j(".deliverFile").html()+" "+value.deliverIndex+"</span></a></td>";
						  // Parse date
						  arrayDate = value.submissionDate.split("-");
						  stringday = arrayDate[2].substr(0,arrayDate[2].indexOf("T"));
						  dateString = stringday+"/"+arrayDate[1]+"/"+arrayDate[0];
						  
						  resultDelivers += "<td>"+dateString+"</td>";
						  totalsum = value.totalPublicTests+value.totalPrivateTests;
						  resultDelivers += "<td>"+totalsum+"</td>";
						  resultDelivers += "<td>";
						  	if(value.compileOK){
						  		resultDelivers +="<span class=\"ok\"><span class=\"invisible\">Ok</span></span>";
						  	}else{
						  		resultDelivers +="<span class=\"ko\"><span class=\"invisible\">Ko</span></span>";
						  	}
						  	resultDelivers +="</td>";
						  	resultDelivers += "<td><div class=\"tests\"><span class=\"ko\">"+value.totalPublicTests+"</span><span class=\"ok\">"+value.passedPublicTests+"</span></div></td>";
						  	resultDelivers += "<td><div class=\"tests\"><span class=\"ko\">"+value.totalPrivateTests+"</span> <span class=\"ok\">"+value.passedPrivateTests+"</span></div></td>";
						  	resultDelivers += "</tr>";
						  	
						  	resultDelivers += '<tr class="expand-child"><td colspan="6"><div id="a'+userId+'_e'+index+'" class="files_tests"><table class="tlevel_3"><thead>';
						  	resultDelivers += "<tr>";
						  	resultDelivers += "<th>"+j(".fileTitle").html()+"</th><th>"+j(".code").html()+"</th><th>"+j(".memori").html()+"</th><th>"+j(".principal").html()+"</th>";
						  	resultDelivers += "</tr></thead><tbody>";
						  	
						  	j.each(value.deliverFiles, function(indexFile, valueFile) {
						  		resultDelivers += "<tr>";
						  		resultDelivers += "<td><a href=\"home!down.html?idDelivers="+index+"&idFile="+indexFile+"&s_aula="+j("#s_aula").val()+"&s_assign="+j("#s_assign").val()+"&s_activ="+j("#s_activ").val()+"&userId="+userId+"\">"+valueFile.relativePath+"</a></td>";
						  		resultDelivers += "<td>";
						  		if(valueFile.isCode){
						  			resultDelivers += "<span class=\"check\" title=\"Code\"></span>";
						  		}
						  		resultDelivers += "</td>";
						  		
						  		resultDelivers += "<td>";
						  		if(valueFile.isReport){
						  			resultDelivers += "<span class=\"check\" title=\"Memori\"></span>";
						  		}
						  		resultDelivers += "</td>";
						  		
						  		resultDelivers += "<td>";
						  		if(valueFile.isMain){
						  			resultDelivers += "<span class=\"check\" title=\"principal\"></span>";
						  		}
						  		resultDelivers += "</td></tr>";
						  	});
						  	resultDelivers += "</tbody></table>";
						  	
						  	resultDelivers += "<div class=\"heading\"><span>"+j(".testPublic").html()+"</span></div>";
						  	if(value.testResults.length >0){
						  	resultDelivers += "<ul>";
						  	j.each(value.testResults, function(indexResult, valueResult) {
						  		if(valueResult.isPublic){
						  			if(valueResult.isPassed){
						  				resultDelivers +="<li><a href=\"#\" target=\"_blank\"><span class=\"ok\"></span>"+valueResult.output+"</a></li>";
						  			}else{
						  				resultDelivers +="<li><a href=\"#\" target=\"_blank\"><span class=\"ko\"></span>"+valueResult.output+"</a></li>";
						  			}
						  		}
						  	});
						  	resultDelivers +="</ul>";
						  	}
						  	resultDelivers += "<div class=\"heading\"><span>"+j(".testPrivate").html()+"</span></div>";
						  	if(value.testResults.length >0){
						  	resultDelivers += "<ul>";
						  	j.each(value.testResults, function(indexResult, valueResult) {
						  		if(!valueResult.isPublic){
						  			if(valueResult.isPassed){
						  				resultDelivers +="<li><a href=\"#\" target=\"_blank\"><span class=\"ok\"></span>"+valueResult.output+"</a></li>";
						  			}else{
						  				resultDelivers +="<li><a href=\"#\" target=\"_blank\"><span class=\"ko\"></span>"+valueResult.output+"</a></li>";
						  			}
						  		}
						  	});
						  	resultDelivers +="</ul>";
						  	}
						  	
						  	resultDelivers +="</div></td></tr>";
				  		}
				  });
				resultDelivers +="</tbody></table>";
				  
				j("#a"+userId).html(resultDelivers);  
				

				j('a.toggle').prepend('<span class="icon"></span>');
				j('a.toggle').click(function(ev) {
					if(j(this).attr("id")!="ajaxDelivers"){
						ev.preventDefault();
						j(this).expandCollapseRow(j(this).attr('rel'));
					}
				});
	
				j('a.collapsed').each(function(){
					j("#" + j(this).attr('rel')).hide();
				});

				j('body').removeClass("loading"); 
			  },
			  type: "POST"
			});
		}
	}
});

	
/* menu*/
		
});

function doBeforeChangeTab(jqXHR, settings){
	//alert('ajax call issued');
}

function doChangeTab(data, textStatus, jqXHR, whichTabIsActive){

	//alert('about to replace contents');

    var jqObj = jQuery(data);
    var theirMain = jqObj.find("#main");
	j('#main').html(theirMain);
	
	j('.ajax-tab').each(function(ind, e){
		var thisTab = j(this);
		var thisHref = thisTab.attr('href');
		var ind = thisHref.indexOf(whichTabIsActive);
		if (ind != -1){
			thisTab.parent().addClass('active');
		} else {
			thisTab.parent().removeClass('active');
		}
	});
	
}

function doCompleteChangeTab(jqXHR, textStatus) {
	//alert('ajax call completed.');	
}

function doErrorChangingTab(jqXHR, textStatus, errorThrown) {
	//alert('error! ' + textStatus);
}
function validate_filename(filename){
	var n=filename.lastIndexOf("\\");
	var string=filename.substr(n+1,filename.length)		
	regexString = /[^\u00e1\u00e9\u00ed\u00f3\u00fa\u00c1\u00c9\u00cd\u00d3\u00da\u00f1\u00d1\u00FC\u00DC]+$/;
	//(/^([a-z]+\..+[a-z]+)$/.test("tesst.uoc"))
	if (!(regexString.test(string))){
		  return false;
	}
	return true;
}

