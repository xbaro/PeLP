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
					<a href="admin-activities!auth.html" id="loginopenapi" class="btnopenapi" ></a>
				</s:if>
				<s:else>
					<div class="profile"> 
							<img src="<s:property value='imageURL'/>" alt="Profile Photo" />
							<h2><s:property value="fullName"/></h2>
							<a href="admin-activities!logout.html" id="logout" class="btn"><s:text name="pelp.exit"></s:text></a>
						</div>
				</s:else>
				
			</div>
		</div>
		<div style="float: left;display: inline;margin: 20px 20px 10px;">
		<a href="admin.html">Semestres</a> | <a href="admin-subjects.html">Assignatures</a> | Activitats
		</div>
	</div>
	<!-- /top -->

	

		<s:form  action="admin-activities.html" cssClass="form_login" theme="simple" >
							
			<fieldset class="fs_admin">
				<label class="hlabel"><s:text name="pelp.subject"></s:text></label>
				<select name="subjectID" id="subject" onchange="forms[0].submit();" >				 
					<s:iterator value="subjectsList" var="subjectItem" >
						<s:if test="%{subjectID == [1].subjectID}"> 
							<option selected="selected" value="<s:property value="subjectID" />"><s:property value="subjectCode" /> - <s:property value="description"/></option>
						</s:if> 
						<s:else> 
							<option value="<s:property value="subjectID"/>">
								<s:property value="subjectCode" /> - <s:property value="description"/>
							</option> 
						</s:else> 
					</s:iterator> 
				</select>
			</fieldset>
			<fieldset class="fs_admin">
				<label class="hlabel">Activitat</label>
				<select name="activityIndex" id="activityIndex" onchange="forms[0].submit();" >				 
					<s:iterator value="activitiesList" >
						<s:if test="%{activityIndex == index}"> 
							<option selected="selected" value="<s:property value="index" />"><s:property value="index" /> - <s:property value="description"/></option>
						</s:if> 
						<s:else> 
							<option value="<s:property value="index"/>">
								<s:property value="index" /> - <s:property value="description"/>
							</option> 
						</s:else> 
					</s:iterator> 
				</select>
			</fieldset>			
		</s:form>
		
		<br><br><br><br><br><br>
		
		<s:if test="%{isTeacher}">
		
		<s:form  action="admin-activities!addActivity.html" cssClass="form_login" theme="simple" >	
			<fieldset class="fs_admin2">
				<s:hidden key="semester"></s:hidden>
				<s:hidden key="subject"></s:hidden>
				<s:hidden key="subjectID"></s:hidden>
				<s:hidden key="activityIndex"></s:hidden>
				<label class="hlabel">Desc CAT</label>
				<div class="in_text">
					<s:textfield name="activityDescriptionCat" style="width: 160px"/>
				</div>
			</fieldset>
			<fieldset class="fs_admin2">
				<label class="hlabel">Desc ES</label>
				<div class="in_text">
					<s:textfield name="activityDescriptionEs" style="width: 160px"/>
				</div>
			</fieldset>
			<fieldset class="fs_admin2" style="width: 120px">
				<label class="hlabel">Data inici</label>
				<div class="in_text">
					<s:textfield name="start" id="txt_start" style="width: 65px"/>
				</div>
			</fieldset>
			<fieldset class="fs_admin2" style="width: 120px">
				<label class="hlabel">Data fi</label>
				<div class="in_text">
					<s:textfield name="end" id="txt_start" style="width: 65px"/>
				</div>
			</fieldset>
			<fieldset class="fs_admin2" style="width: 120px">	
				<label class="hlabel">Max entregues</label>
				<div class="in_text">
					<s:textfield name="maxDelivers" id="txt_maxDelivers" style="width: 40px"/>
				</div>
			</fieldset>
			<fieldset class="fs_admin2" style="width: 120px">	
				<label class="hlabel">progLangCode</label>
				<div class="in_text">
					<s:textfield name="progLangCode" id="txt_progLangCode" style="width: 40px"/>
				</div>
			</fieldset>		
			
			<s:submit value="Insertar" cssClass="btn" style="margin-top: 40px;"></s:submit>
		</s:form>
	
		<table>
			<thead>	
				<tr>
					<td>Test</td>
					<td>Input</td>
					<td>Output</td>
					<td></td>
				</tr>
			</thead>
		
			<s:iterator value="testList" >
				<tr>
					<td><s:property value="description" /> </td> 
					<td><s:property value="inputText" />  </td>
					<td><s:property value="expectedOutput" />  </td>
					<td> <a href="admin-activities!removeTest.html?subject=<s:property value="subject" />&activityIndex=<s:property value="activityIndex" />&testIndex=<s:property value="testID.index" />">desactivar</a></td>
				</tr> 	 
			</s:iterator>		 
		</table>
		
		<s:form  action="admin-activities!addTest.html" cssClass="form_login" theme="simple" >	
			<fieldset class="fs_admin2">
				<s:hidden key="semester"></s:hidden>
				<s:hidden key="subject"></s:hidden>
				<s:hidden key="subjectID"></s:hidden>
				<s:hidden key="activityIndex"></s:hidden>
				<label class="hlabel">Desc CAT</label>
				<div class="in_text">
					<s:textfield name="activityDescriptionCat" style="width: 160px"/>
				</div>
			</fieldset>
			<fieldset class="fs_admin2">
				<label class="hlabel">Desc ES</label>
				<div class="in_text">
					<s:textfield name="activityDescriptionEs" style="width: 160px"/>
				</div>
			</fieldset>
			<fieldset class="fs_admin2" style="width: 120px">
				<label class="hlabel">Input</label>
				<div class="in_text">
					<s:textfield name="inputStr" id="txt_input" style="width: 65px"/>
				</div>
			</fieldset>
			<fieldset class="fs_admin2" style="width: 120px">
				<label class="hlabel">Output</label>
				<div class="in_text">
					<s:textfield name="expectedOutputStr" id="txt_Output" style="width: 65px"/>
				</div>
			</fieldset>
			
			
			<s:submit value="Insertar" cssClass="btn" style="margin-top: 40px;"></s:submit>
		</s:form>
	
	</s:if>
</div>
<div class="modal"></div>


<!-- /container -->
</body>
</html>