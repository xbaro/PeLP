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
					<a href="admin-subjects!auth.html" id="loginopenapi" class="btnopenapi" ></a>
				</s:if>
				<s:else>
					<div class="profile"> 
							<img src="<s:property value='imageURL'/>" alt="Profile Photo" />
							<h2><s:property value="fullName"/></h2>
							<a href="admin-subjects!logout.html" id="logout" class="btn"><s:text name="pelp.exit"></s:text></a>
						</div>
				</s:else>
				
			</div>
		</div>
		<div style="float: left;display: inline;margin: 20px 20px 10px;">
		<a href="admin.html">Semestres</a> | Assignatures | <a href="admin-activities.html">Activitats</a>
		</div>
	</div>
	<!-- /top -->

	<s:if test="%{isAdmin}">

		<s:form  action="admin-subjects.html" cssClass="form_login" theme="simple" >
			<fieldset class="fs_admin">
				<label class="hlabel"><s:text name="pelp.semestre"></s:text></label>
				<select name="semester" id="semester" onchange="forms[0].submit();" >				 
					<s:iterator value="semesterList" >
						<s:if test="%{semester == ID}"> 
							<option selected="selected" value="<s:property value="ID" />"><s:property value="ID"/></option>
						</s:if> 
						<s:else> 
							<option value="<s:property value="ID"/>">
								<s:property value="ID"/>
							</option> 
						</s:else> 
					</s:iterator> 
				</select>
			</fieldset>
		</s:form>
		
		<s:form  action="admin-subjects!add.html" cssClass="form_login" theme="simple" >	
			<fieldset class="fs_admin">
			<s:hidden key="semester"></s:hidden>
				<label class="hlabel"><s:text name="pelp.subject"></s:text></label>
				<div class="in_text">
					<s:textfield name="subject" id="txt_subject" style="width: 160px"/>
				</div>
			</fieldset>

			<s:submit value="Insertar" cssClass="btn" style="margin-top: 40px;"></s:submit>
		</s:form>
		
		
		<table>
			<thead>	
				<tr>
					<td><s:text name="pelp.subject"></s:text></td>
					<td></td>
				</tr>
			</thead>
		
		<s:iterator value="subjectList" >
			<tr>
				<td><s:property value="ID" /> - <s:property value="description" /> </td> <td> <a href="admin-subjects!deactivate.html?subject=<s:property value="ID" />">desactivar</a></td>
			</tr> 	 
		</s:iterator>
		</table>

		<s:form  action="admin-subjects!copyFromPreviousSemester.html" cssClass="form_login" theme="simple" >
			<fieldset class="fs_admin">
				<s:hidden key="semester"></s:hidden>
				<s:submit value="Copiar" cssClass="btn" style="margin-top: 10px;"></s:submit>
			</fieldset>
		</s:form>
			
	</s:if>
</div>
<div class="modal"></div>


<!-- /container -->
</body>
</html>