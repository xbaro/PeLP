<%@taglib prefix="s" uri="/struts-tags" %>

<s:set id="contextPath"  value="#request.get('javax.servlet.forward.context_path')" />


<!DOCTYPE html>
<!--[if lt IE 7 ]> <html lang="ca" class="ie ie6"> <![endif]-->
<!--[if IE 7 ]>    <html lang="ca" class="ie ie7"> <![endif]-->
<!--[if IE 8 ]>    <html lang="ca" class="ie ie8"> <![endif]-->
<!--[if IE 9 ]>    <html lang="ca" class="ie ie9"> <![endif]-->
<!--[if (gt IE 9)|!(IE)]><!--> <html lang="ca"> <!--<![endif]-->
<head>
	<meta charset="utf-8" />
	<title>
			<s:text name="pelp.title.admin"/>
	</title>
	<meta name="description" content="Plataforma on-line per l'aprenentatge de llenguatges de programació" />
	<meta name="keywords" content="" />
	<meta name="robots" content="index, follow" /> 
	<link rel="stylesheet" type="text/css" href="css/main.css" media="all" />
	<link rel="stylesheet" type="text/css" href="css/messi.min.css" media="all" />

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
				<h1><a href="#" title="<s:text name='pelp.init'/>"><img src="img/logo_pelp.png" alt="Pelp" /></a></h1>
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
				<s:if test="%{fullName == null}">
					<a href="admin!auth.html" id="loginopenapi" class="btnopenapi" ></a>
				</s:if>
				<s:else>
					<div class="profile"> 
							<img src="<s:property value='imageURL'/>" alt="Profile Photo" />
							<h2><s:property value="fullName"/></h2>
							<a href="admin!logout.html" id="logout" class="btn"><s:text name="pelp.exit"></s:text></a>
						</div>
				</s:else>
				
			</div>
		</div>
		<div style="float: left;display: inline;margin: 20px 20px 10px;">
		Semestres | <a href="admin-subjects.html">Assignatures</a> | <a href="admin-activities.html">Activitats</a>
		</div>
	</div>
	<!-- /top -->

	<s:if test="%{isAdmin}">

		<s:form  action="admin!add.html" cssClass="form_login" theme="simple">
			<fieldset class="fs_admin">
				<label class="hlabel"><s:text name="pelp.semestre"></s:text></label>
				<div class="in_text">
					<s:textfield name="semester" id="txt_semester" style="width: 160px"/>
				</div>
			</fieldset>
			<fieldset class="fs_admin">
				<label class="hlabel"><s:text name="pelp.semester.start"></s:text></label>
				<div class="in_text">
					<s:textfield name="start" id="txt_start" style="width: 160px"/>
				</div>
			</fieldset>
			<fieldset class="fs_admin">
				<label class="hlabel"><s:text name="pelp.semester.end"></s:text></label>
				<div class="in_text">
					<s:textfield name="end" id="txt_end" style="width: 160px"/>
				</div>				
			</fieldset>
			<s:submit id="login" value="Insertar" cssClass="btn" style="margin-top: 40px;"></s:submit>
		</s:form>
	
		<table>
			<thead>	
				<tr>
					<td><s:text name="pelp.semestre"></s:text></td>
					<td></td>
				</tr>
			</thead>
		
		<s:iterator value="semesterList" >
			<tr>
				<td><s:property value="Semester" /></td> <td> <a href="admin!remove.html?semester=<s:property value="Semester" />">eliminar</a></td>
			</tr> 	 
		</s:iterator>
		 
		</table>
	
	</s:if>
</div>
<div class="modal"></div>


<!-- /container -->
</body>
</html>