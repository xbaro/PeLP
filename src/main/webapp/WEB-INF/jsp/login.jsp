<%@page import="edu.uoc.pelp.actions.LoginAction"%>
<%@taglib prefix="s" uri="/struts-tags" %>
<%@taglib prefix="sj" uri="/struts-jquery-tags" %>

<!DOCTYPE html>
<!--[if lt IE 7 ]> <html lang="ca" class="ie ie6"> <![endif]-->
<!--[if IE 7 ]>    <html lang="ca" class="ie ie7"> <![endif]-->
<!--[if IE 8 ]>    <html lang="ca" class="ie ie8"> <![endif]-->
<!--[if IE 9 ]>    <html lang="ca" class="ie ie9"> <![endif]-->
<!--[if (gt IE 9)|!(IE)]><!--> 
<html lang="ca"> <!--<![endif]-->
    <head>
        <meta charset="utf-8" />
        <title>Pelp Administration</title>
        <meta name="description" content="Plataforma on-line per l’aprenentatge de llenguatges de programació" />
        <meta name="keywords" content="" />
        <meta name="robots" content="index, follow" /> 
        <link rel="stylesheet" type="text/css" href="/pelp/css/main.css" media="all" />
        <!--"#request.get('javax.servlet.forward.context_path')"-->
        <s:set id="contextPath"  value="#request.get('javax.servlet.forward.context_path')" />
        <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js"></script>  
        <script type="text/javascript">window.jQuery || document.write("<script type='text/javascript' src='<s:property value="contextPath"/>/js/jquery-1.7.2.min.js'>\x3C/script>")</script>
        <script type="text/javascript" src="<s:property value="contextPath"/>/js/jquery.easing.1.3.js"></script>
        <script type="text/javascript" src="<s:property value="contextPath"/>/js/jquery.customforminput.min.js"></script>
        <script type="text/javascript" src="<s:property value="contextPath"/>/js/jquery.placeholder.min.js"></script>
        <script type="text/javascript" src="<s:property value="contextPath"/>/js/jquery.tablesorter.min.js"></script>
        <script type="text/javascript" src="<s:property value="contextPath"/>/js/pelp.js"></script>
        <sj:head jqueryui="true"/>
    </head>
    <body>
        <div id="container">

            <!-- accessibility -->
            <div id="accessibility">
                <a href="#main" accesskey="s" title="Accés directe al contingut">Accés directe al contingut</a> | 
                <a href="#menu" accesskey="n" title="Accés directe al menú de navegació">Accés directe al menú de navegació</a> 
            </div>
            <!-- /accessibility -->

            <!-- head -->
            <div id="head-container">
                <div id="head">
                    <div id="pelp">
                        <h1><a href="#" title="Inicio Pelp"><img src="img/logo_pelp.png" alt="Pelp" /></a></h1>
                        <h2>Plataforma on-line per l’aprenentatge de llenguatges de programació</h2>
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

                        <div class="profile">
                            <img src="<s:property value="userPhoto"/>" alt="Profile Photo" />
                            <h2>
                                <s:property value="userFullName"/>
                            </h2>
                            <a href="javascript:void(0);" id="logout" class="btn">Salir</a>
                        </div>

                    </div>
                </div>
            </div>
            <!-- /top -->
            <!-- menu -->
            <div id="menu-container">
                <div id="menu">
                    <ul class="menu">
                        <li><a href="#">Entorno programación</a></li>
                        <li class="active"><a href="#">Entregas</a></li>
                    </ul>
                </div>
            </div>
            <!-- /menu -->

            <!-- main -->
            <div id="main">
                <h1>List of subjects</h1>
                <s:iterator value="listSubjects" >
                    <p>
                        <s:property value="ID.Code" />-<s:property value="ID.Semester" />=><s:property value="Description"/></option>
                    </p>
                </s:iterator> 
            </div>
            <!-- /main -->

        </div>
        <!-- /container -->


    </body>
</html>
<!--

        HttpSession s=request.getSession();
        
        if(request.getSession().getAttribute("authTokenUOC")==null) {
            request.getSession().setAttribute("authUOC", "request");
            response.sendRedirect(request.getRequestURI());
            return;
        }
        %>
-->