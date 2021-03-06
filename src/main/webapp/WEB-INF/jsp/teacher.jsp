<%@taglib prefix="s" uri="/struts-tags" %>
<!DOCTYPE html>
<!--[if lt IE 7 ]> <html lang="ca" class="ie ie6"> <![endif]-->
<!--[if IE 7 ]>    <html lang="ca" class="ie ie7"> <![endif]-->
<!--[if IE 8 ]>    <html lang="ca" class="ie ie8"> <![endif]-->
<!--[if IE 9 ]>    <html lang="ca" class="ie ie9"> <![endif]-->
<!--[if (gt IE 9)|!(IE)]><!--> <html lang="ca"> <!--<![endif]-->
<head>
	<meta charset="utf-8" />
	<title><s:text name="pelp.web.teacher"></s:text></title>
	<meta name="description" content="Plataforma on-line per l’aprenentatge de llenguatges de programació" />
	<meta name="keywords" content="" />
	<meta name="robots" content="index, follow" /> 
	<link rel="stylesheet" type="text/css" href="css/main.css" media="all" />
	<s:set id="contextPath"  value="#request.get('javax.servlet.forward.context_path')" />
	<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js"></script>  
	<script type="text/javascript">window.jQuery || document.write("<script type='text/javascript' src='<s:property value="contextPath"/>/js/jquery-1.7.2.min.js'>\x3C/script>")</script>
	<script type="text/javascript" src="<s:property value="contextPath"/>/js/jquery.easing.1.3.js"></script>
	<script type="text/javascript" src="<s:property value="contextPath"/>/js/jquery.customforminput.min.js"></script>
	<script type="text/javascript" src="<s:property value="contextPath"/>/js/jquery.placeholder.min.js"></script>
	<script type="text/javascript" src="<s:property value="contextPath"/>/js/jquery.tablesorter.min.js"></script>
	<script type="text/javascript" src="<s:property value="contextPath"/>/js/jquery.ba-bbq.min.js"></script>
	<script type="text/javascript" src="<s:property value="contextPath"/>/js/pelp.js"></script>
</head>
<body>

<!-- container -->
<div id="container">

	<!-- accessibility -->
	<div id="accessibility">
		<a href="#main" accesskey="s" title="<s:text name='pelp.acces'></s:text>"> <s:text name="pelp.acces"></s:text> </a> | 
		<a href="#menu" accesskey="n" title="<s:text name='pelp.acces.nav'></s:text>"> <s:text name="pelp.acces.nav"></s:text> </a> 
	</div>
	<!-- /accessibility -->

	<!-- head -->
	<div id="head-container">
		<div id="head">
			<div id="pelp">
				<h1><a href="teacher.html" title="<s:text name='pelp.init'></s:text>"><img src="img/logo_pelp.png" alt="Pelp" /></a></h1>
				<h2><s:text name="pelp.title"></s:text></h2>
			</div>
			<div id="uoc">
				<a href="http://www.uoc.edu" title="UOC"><img src="img/logo_uoc.png" alt="UOC" /></a>
			</div>
		</div>
	</div>
	<!-- /head -->

	<!-- top -->
	<div id="top-container">
		<div id="top">

			<div id="user">
				<s:if test="%{imageURL == null}">
					<s:form  action="teacher!auth.html" cssClass="form_login" id="form_login" theme="simple">
		<!-- 				<form action="/" method="POST" class="form_login" id="form_login"> -->
							<fieldset>
							<s:textfield name="username" id="username" label="username"></s:textfield>
							<s:password name="password" id="password" label="password"></s:password>
		<!-- 						<input type="text" id="username" name="username" placeholder="Nom d'usuari"  /> -->
		<!-- 						<input type="password" id="password" name="password" placeholder="Contrasenya"  /> -->
		<!-- 						<input type="submit" id="login" name="login" value="Accedir" class="btn" /> -->
								<s:submit id="login" value="Accedir" cssClass="btn"></s:submit>
							</fieldset>
		<!-- 				</form> -->
					</s:form>
				</s:if>
				<s:else>
					<div class="profile"> 
							<img src="<s:property value='imageURL'/>" alt="Profile Photo" />
							<h2><s:property value="fullName"/></h2>
							<a href="teacher!logout.html" id="logout" class="btn"><s:text name="pelp.exit"></s:text></a>
						</div>
				</s:else>
			</div>
			<form action="" method="POST" class="form_filters" id="form_filters">
				<fieldset>
					 <select name="s_assign" id="s_assign">
					 	<option value=""><s:text name="pelp.assigment"></s:text> </option>
						<s:iterator value="listSubjects" >
							<s:if test="%{s_assign == SubjectID}"> <option selected="selected" value="<s:property value="SubjectID" />"><s:property value="Description"/></option></s:if> 
							<s:else> <option value="<s:property value="SubjectID" />"><s:property value="Description"/></option> </s:else> 
						</s:iterator> 
					</select>
					<select name="s_aula" id="s_aula">
						<option value=""><s:text name="pelp.classroom"></s:text> </option>
						<s:iterator value="listClassroms">
							<s:if test="%{s_aula == index}"><option selected="selected" value="<s:property value="index" />"><s:text name="pelp.classroom"></s:text> <s:property value="Index" /></option></s:if>
							<s:else><option value="<s:property value="index" />"><s:text name="pelp.classroom"></s:text> <s:property value="Index" /></option></s:else>
						</s:iterator>
					</select>
					<select name="s_activ" id="s_activ">
						<option value=""><s:text name="pelp.activiti"></s:text> </option>
						<s:iterator value="listActivity" status="statsa">
							<s:if test="%{s_activ == index}"><option selected="selected" value="<s:property value="index" />"><s:property value="description" /></option></s:if>
							<s:else><option value="<s:property value="index" />"><s:property value="description" /></option></s:else>
						</s:iterator>
					</select>
					<input type="submit" id="send_filters" name="send_filters" value="Enviar" class="btn"/>
				</fieldset>
			</form>
		</div>
	</div>
	<!-- /top -->

	<!-- menu -->
	<div id="menu-container">
		<div id="menu">
			<ul class="menu">
<!-- 				<li><a href="#">Entorno programación</a></li> -->
				<li class="active"><a href="teacher.html"><s:text name="pelp.delivers"></s:text> </a></li>
			</ul>
		</div>
	</div>
	<!-- /menu -->

	<!-- main -->
	<div id="main">

		<h4><span>Inicio: 20/06/2012</span> <span>Final: 10/07/2012</span></h4>

		<!-- tProfesor -->
		<table id="tProfesor" class="tablesorter tlevel_1">
			<thead class="thead">
				<tr>
					<th><s:text name="pelp.deliver"></s:text> </th>
					<th><s:text name="pelp.date"></s:text> </th>
					<th><s:text name="pelp.replis"></s:text> </th>
					<th><s:text name="pelp.compile"></s:text> </th>
					<th><s:text name="pelp.test.public"></s:text> </th>
					<th><s:text name="pelp.test.private"></s:text> </th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td><a href="#" class="toggle collapsed" rel="a1"><span class="lbl">Alumno 1</span></a></td>
					<td><span class="tmp lbl">01/07/12</span></td>
					<td><span class="tmp lbl">12</span></td>
					<td><span class="tmp ko"><span class="lbl invisible">ko</span></span></td>
					<td><div class="tests"><span class="tmp lbl ko">15</span></span></td>
					<td><div class="tests"><span class="tmp lbl ko">14</span> <span class="tmp lbl ok">2</span></div></td>
				</tr>
				<tr class="expand-child">
					<td colspan="6">

						<div id="a1" class="entregas">
							<table class="tlevel_2">
								<tbody>
									<tr>
										<td><a href="#" class="toggle expanded" rel="a1_e3"><span class="lbl">Entrega 3</span></a></td>
										<td>01/07/12</td>
										<td>12</td>
										<td><span class="ko"><span class="invisible">ko</span></span></td>
										<td><div class="tests"><span class="ko">15</span></div></td>
										<td><div class="tests"><span class="ko">14</span> <span class="ok">2</span></div></td>
									</tr>
									<tr class="expand-child">
										<td colspan="6">

											<div id="a1_e3" class="files_tests">
												<table class="tlevel_3">
													<thead>
														<tr>
															<th>Ficheros</th>
															<th>Código</th>
															<th>Memoria</th>
															<th>F. Principal</th>
														</tr>
													</thead>
													<tbody>
														<tr>
															<td><a href="#">Lorem ipsum dolor sit amet</a></td>
															<td><span class="check" title="Código"></span></td>
															<td></td>
															<td></td>
														</tr>
														<tr>
															<td><a href="#">Cras egestas elementum augue</a></td>
															<td><span class="check" title="Código"></span></td>
															<td><span class="check" title="Memoria"></span></td>
															<td></td>
														</tr>
														<tr>
															<td><a href="#">Cras egestas elementum augue</a></td>
															<td><span class="check" title="Código"></span></td>
															<td></td>
															<td><span class="check" title="F. Principal"></span></td>
														</tr>
													</tbody>
												</table>
												<div class="heading"><span>Tests Publicos</span></div>
												<ul>
													<li><a href="test_info_ko.html" target="_blank"><span class="ko"></span>Cras egestas elementum augue</a></li>
													<li><a href="test_info_ok.html" target="_blank"><span class="ok"></span>Lorem ipsum dolor sit amet</a></li>
													<li><a href="test_info_ok.html" target="_blank"><span class="ok"></span>Lorem ipsum dolor sit amet</a></li>
												</ul>
												<div class="heading"><span>Tests Privados</span></div>
												<ul>
													<li><a href="test_info_ok.html" target="_blank"><span class="ok"></span>Lorem ipsum dolor sit amet</a></li>
													<li><a href="test_info_ko.html" target="_blank"><span class="ko"></span>Lorem ipsum dolor sit amet</a></li>
												</ul>
											</div>

										</td>
									</tr>
									<tr>
										<td><a href="#" class="toggle collapsed" rel="a1_e2"><span class="lbl">Entrega 2</span></a></td>
										<td>01/07/12</td>
										<td>12</td>
										<td><span class="ok"><span class="invisible">ok</span></span></td>
										<td><div class="tests"><span class="ok">15</span></div></td>
										<td><div class="tests"><span class="ko">14</span> <span class="ok">2</span></div></td>
									</tr>
									<tr class="expand-child">
										<td colspan="6">

											<div id="a1_e2" class="files_tests">
												<div class="heading"><span>Tests Públicos</span></div>
												<ul>
													<li><a href="test_info_ko.html" target="_blank"><span class="ko"></span>Cras egestas elementum augue</a></li>
													<li><a href="test_info_ok.html" target="_blank"><span class="ok"></span>Lorem ipsum dolor sit amet</a></li>
													<li><a href="test_info_ok.html" target="_blank"><span class="ok"></span>Lorem ipsum dolor sit amet</a></li>
												</ul>
												<div class="heading"><span>Tests Privados</span></div>
												<ul>
													<li><a href="test_info_ok.html" target="_blank"><span class="ok"></span>Lorem ipsum dolor sit amet</a></li>
													<li><a href="test_info_ko.html" target="_blank"><span class="ko"></span>Lorem ipsum dolor sit amet</a></li>
												</ul>
											</div>

										</td>
									</tr>
									<tr>
										<td><a href="#" class="toggle collapsed" rel="a1_e1"><span class="lbl">Entrega 1</span></a></td>
										<td>01/07/12</td>
										<td>12</td>
										<td><span class="ok"><span class="invisible">ok</span></span></td>
										<td><div class="tests"><span class="ok">15</span></div></td>
										<td><div class="tests"><span class="ko">14</span> <span class="ok">2</span></div></td>
									</tr>
									<tr class="expand-child">
										<td colspan="6">

											<div id="a1_e1" class="files_tests">
												<div class="heading"><span>Tests Públicos</span></div>
												<ul>
													<li><a href="test_info_ko.html" target="_blank"><span class="ko"></span>Cras egestas elementum augue</a></li>
													<li><a href="test_info_ok.html" target="_blank"><span class="ok"></span>Lorem ipsum dolor sit amet</a></li>
													<li><a href="test_info_ok.html" target="_blank"><span class="ok"></span>Lorem ipsum dolor sit amet</a></li>
												</ul>
												<div class="heading"><span>Tests Privados</span></div>
												<ul>
													<li><a href="test_info_ok.html" target="_blank"><span class="ok"></span>Lorem ipsum dolor sit amet</a></li>
													<li><a href="test_info_ko.html" target="_blank"><span class="ko"></span>Lorem ipsum dolor sit amet</a></li>
												</ul>
											</div>

										</td>
									</tr>
								</tbody>
							</table>
						</div>

					</td>
				</tr>
				<tr>
					<td><a href="#" class="toggle collapsed" rel="a2"><span class="lbl">Alumno 2</span></a></td>
					<td><span class="tmp lbl">03/07/12</span></td>
					<td><span class="tmp lbl">3</span></td>
					<td><span class="tmp ok"><span class="lbl invisible">ok</span></span></td>
					<td><div class="tests"><span class="tmp lbl ok">1</span></div></td>
					<td><div class="tests"><span class="tmp lbl ko">2</span></div></td>
				</tr>
				<tr class="expand-child">
					<td colspan="6">

						<div id="a2" class="entregas">
							<table class="tlevel_2">
								<tbody>
									<tr>
										<td><a href="#" class="toggle expanded" rel="a2_e2"><span class="lbl">Entrega 2</span></a></td>
										<td>03/07/12</td>
										<td>3</td>
										<td><span class="ok"><span class="invisible">ko</span></span></td>
										<td><div class="tests"><span class="ok">1</span></div></td>
										<td><div class="tests"><span class="ko">2</span></div></td>
									</tr>
									<tr class="expand-child">
										<td colspan="6">

											<div id="a2_e2" class="files_tests">
												<table class="tlevel_3">
													<thead>
														<tr>
															<th>Ficheros</th>
															<th>Código</th>
															<th>Memoria</th>
															<th>F. Principal</th>
														</tr>
													</thead>
													<tbody>
														<tr>
															<td><a href="#">Lorem ipsum dolor sit amet</a></td>
															<td><span class="check" title="Código"></span></td>
															<td></td>
															<td></td>
														</tr>
														<tr>
															<td><a href="#">Cras egestas elementum augue</a></td>
															<td></td>
															<td><span class="check" title="Memoria"></span></td>
															<td></td>
														</tr>
													</tbody>
												</table>
												<div class="heading"><span>Tests Públicos</span></div>
												<ul>
													<li><a href="test_info_ko.html" target="_blank"><span class="ko"></span>Cras egestas elementum augue</a></li>
													<li><a href="test_info_ok.html" target="_blank"><span class="ok"></span>Lorem ipsum dolor sit amet</a></li>
												</ul>
												<div class="heading"><span>Tests Privados</span></div>
												<ul>
													<li><a href="test_info_ok.html" target="_blank"><span class="ok"></span>Lorem ipsum dolor sit amet</a></li>
													<li><a href="test_info_ko.html" target="_blank"><span class="ko"></span>Lorem ipsum dolor sit amet</a></li>
												</ul>
											</div>

										</td>
									</tr>
									<tr>
										<td><a href="#" class="toggle collapsed" rel="a2_e1"><span class="lbl">Entrega 1</span></a></td>
										<td>01/07/12</td>
										<td>12</td>
										<td><span class="ok"><span class="invisible">ok</span></span></td>
										<td><div class="tests"><span class="ok">15</span></div></td>
										<td><div class="tests"><span class="ko">14</span> <span class="ok">2</span></div></td>
									</tr>
									<tr class="expand-child">
										<td colspan="6">

											<div id="a2_e1" class="files_tests">
												<div class="heading"><span>Tests Públicos</span></div>
												<ul>
													<li><a href="test_info_ko.html" target="_blank"><span class="ko"></span>Cras egestas elementum augue</a></li>
													<li><a href="test_info_ok.html" target="_blank"><span class="ok"></span>Lorem ipsum dolor sit amet</a></li>
													<li><a href="test_info_ok.html" target="_blank"><span class="ok"></span>Lorem ipsum dolor sit amet</a></li>
												</ul>
												<div class="heading"><span>Tests Privados</span></div>
												<ul>
													<li><a href="test_info_ok.html" target="_blank"><span class="ok"></span>Lorem ipsum dolor sit amet</a></li>
													<li><a href="test_info_ko.html" target="_blank"><span class="ko"></span>Lorem ipsum dolor sit amet</a></li>
												</ul>
											</div>

										</td>
									</tr>
								</tbody>
							</table>
						</div>

					</td>
				</tr>
			</tbody>
		</table>
		<!-- /tProfesor -->

	</div>
	<!-- /main -->

</div>
<!-- /container -->

</body>
</html>