
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"  xmlns:atidlm="http://www.arbortext.com/namespace/atidlm">

    <xsl:template match="struckoutwords|insertwords">
        <xsl:apply-templates/>
    </xsl:template>


    <xsl:template name="quote">
        <xsl:if test="@quote = '1'">“</xsl:if>
    </xsl:template>

    <xsl:template name="parentquote">
        <xsl:if test="../@quote = '1'">“</xsl:if>
    </xsl:template>

    <xsl:template match="quote.in">
        <q class="quote-in"><xsl:if test="@quote = '1'">“</xsl:if>
        <xsl:apply-templates/>
        <xsl:if test="@quote = '1'">”</xsl:if></q>
    </xsl:template>


    <xsl:template match="act">
        <div class="legislation">
            <div>
                <div class="act top-level">
                     <xsl:attribute name="id">
                        <xsl:value-of select="@id"/>
                    </xsl:attribute>
                    <xsl:if test="@terminated = 'repealed'">
                       <xsl:attribute name="class">repealed</xsl:attribute>
                    </xsl:if>
                    <xsl:call-template name="current"/>
                    <xsl:apply-templates select="cover"/>
                    <xsl:apply-templates select="billdetail"/>
                    <xsl:apply-templates select="front"/>
                    <xsl:apply-templates select="body"/>
                    <xsl:apply-templates select="schedule.group"/>
                    <xsl:apply-templates select="end"/>
                </div>
            </div>
        </div>
    </xsl:template>


    <xsl:template match="regulation">
        <div class="legislation">
            <div>
            <div class="regulation top-level">
                    <xsl:attribute name="id">
                        <xsl:value-of select="@id"/>
                    </xsl:attribute>
                     <xsl:if test="@terminated = 'repealed'">
                       <xsl:attribute name="class">repealed</xsl:attribute>
                    </xsl:if>
                        <xsl:call-template name="current"/>
                      <xsl:apply-templates select="cover"/>
                       <xsl:apply-templates select="front"/>
                     <xsl:apply-templates select="body"/>
                     <xsl:apply-templates select="schedule.group"/>
                     <xsl:apply-templates select="end"/>
                </div>

            </div>
        </div>
    </xsl:template>


    <xsl:template match="cover">
        <div class="cover reprint">
            <xsl:if test="@data-hook!=''">
                <xsl:attribute name="data-hook">
                    <xsl:value-of select="@data-hook"/>
                </xsl:attribute>
                <xsl:attribute name="data-hook-length">
                    <xsl:value-of select="@data-hook-length"/>
                </xsl:attribute>
            </xsl:if>
           <xsl:if test=" ../@formatted.reprint != '' and ../@old-version != '' ">
                <p class="reprint-date">
                    Reprint as at <xsl:value-of select="../@formatted.reprint" />
                </p>
            </xsl:if>
            <h1 class="title"><xsl:value-of select="title"/></h1>
            <xsl:if test="../@sr.no">
                <p class="reprint-sr-number">(SR <xsl:value-of select="../@year" />/<xsl:value-of select="../@sr.no" />)</p>
                <p class="gg"><xsl:value-of select="gg" /></p>
                <xsl:apply-templates select="made" />
            </xsl:if>
            <xsl:if test="../@act.no">
                <xsl:call-template name='act-cover'/>
            </xsl:if>
            <xsl:apply-templates />
        </div>
    </xsl:template>

    <xsl:template match="cover/title|cover/reprint-date|cover/assent|cover/commencement">
    </xsl:template>


    <xsl:template name="act-cover">
        <table class="cover-properties">
            <colgroup>
                <col class="cover-properties-column-1" width="47.6%"/>
                <col class="cover-properties-column-2" width="4.8%"/>
                <col class="cover-properties-column-3" width="47.6%"/>
            </colgroup>
            <tbody>
                <tr>
                    <td><div class="document-type">
                        <xsl:call-template name="act-type">
                            <xsl:with-param name="type"><xsl:value-of select="../@act.type"/></xsl:with-param>
                    </xsl:call-template></div></td><td></td>
                    <td><div class="legislation-number"><xsl:value-of select="../@year"/> No <xsl:value-of select="../@act.no"/></div></td></tr>
                <xsl:if test="../@formatted.assent != ''">
                    <tr>
                        <td><div class="assent-date-title">Date of assent</div></td>
                        <td></td><td><div class="assent-date"><xsl:value-of select="../@formatted.assent" /></div></td>
                </tr></xsl:if>
                <xsl:if test="commencement/text() != ''">
                    <tr>
                        <td><div class="commencement-title">Commencement</div></td>
                        <td></td><td><div class="commencement"><xsl:value-of select="commencement"/></div></td>
                    </tr>
                </xsl:if>
            </tbody>
        </table>
    </xsl:template>

    <xsl:template name="act-type">
        <xsl:param name="type" />
        <xsl:choose>
            <xsl:when test="$type = 'public'">Public Act</xsl:when>
            <xsl:when test="$type = 'private'">Private Act</xsl:when>
            <xsl:when test="$type = 'local'">Local Act</xsl:when>
            <xsl:when test="$type = 'provincial'">Provincial Act</xsl:when>
            <xsl:when test="$type = 'imperial'">Imperial Act</xsl:when>
            <xsl:otherwise>Act</xsl:otherwise>
        </xsl:choose>
    </xsl:template>


    <xsl:template match="contents">
    </xsl:template>

    <xsl:template match="made">
        <div class="made">
            <h2 class="made"><xsl:value-of select="heading"/></h2>
            <p class="made-at"><xsl:value-of select="made.at"/></p>
            <p class="made-present"><xsl:value-of select="made.present"/></p>
        </div>

        </xsl:template>

    <xsl:template match="cover.reprint-note">
        <div class="cover-reprint-note">
            <hr class="cover-reprint-note"/>
                <h6 class="cover-reprint-note">Note</h6>
                 <xsl:apply-templates />
                <hr class="cover-reprint-note"/>
        </div>
    </xsl:template>

    <xsl:template match="admin-office">
        <p class="admin-office"><xsl:value-of select="."/></p>
    </xsl:template>


    <xsl:template match="front">
        <div class="front">
            <xsl:attribute name="id">
                <xsl:value-of select="@id"/>
            </xsl:attribute>
            <div class="long-title">
                <xsl:apply-templates select="long-title/para/textlong-title/para/label-para|pursuant"/>


                <xsl:if test="long-title[@deletion-status='repealed']">
                    <p class="deleted para-deleted">[Repealed]</p>
                </xsl:if>
                <xsl:apply-templates select="long-title/notes"/>
             </div>
        </div>
    </xsl:template>

    <xsl:template match="body[@prov-type='regulation']/heading">
        <h2 class="regulation-type"><xsl:value-of select="."/></h2>
    </xsl:template>

    <xsl:template match="body">
        <div class="body">
            <xsl:attribute name="id">
                <xsl:value-of select="@id"/>
            </xsl:attribute>
                <xsl:if test="@data-hook!=''">
                    <xsl:attribute name="data-hook">
                        <xsl:value-of select="@data-hook"/>
                    </xsl:attribute>
                    <xsl:attribute name="data-hook-length">
                        <xsl:value-of select="@data-hook-length"/>
                    </xsl:attribute>
                </xsl:if>
             <xsl:apply-templates />
        </div>
    </xsl:template>


    <xsl:template match="part">
        <div>
             <xsl:attribute name="id">
                <xsl:value-of select="@id"/>
            </xsl:attribute>
                <xsl:if test="@data-hook!=''">
                    <xsl:attribute name="data-hook">
                        <xsl:value-of select="@data-hook"/>
                    </xsl:attribute>
                    <xsl:attribute name="data-hook-length">
                        <xsl:value-of select="@data-hook-length"/>
                    </xsl:attribute>
                </xsl:if>
             <xsl:attribute name="class">
                <xsl:choose>
                    <xsl:when test="@quote='1'">part first</xsl:when>
                    <xsl:otherwise>part</xsl:otherwise>
                </xsl:choose>
                <!-- will loose previous class -->
            </xsl:attribute>
            <xsl:call-template name="current">
                <xsl:with-param name="class">part</xsl:with-param>
            </xsl:call-template>


                <xsl:attribute name="data-location-no-path"></xsl:attribute>
                <xsl:choose>
                     <xsl:when test="ancestor::*[@quote]  or ancestor::amend">
                     </xsl:when>
                    <xsl:when test="ancestor::schedule">
                        <xsl:attribute name="data-location">, cl <xsl:value-of select="normalize-space(./prov/label)"/></xsl:attribute>
                    </xsl:when>
                        <xsl:otherwise>
                        <xsl:attribute name="data-location">s <xsl:value-of select="normalize-space(./prov/label)"/></xsl:attribute>
                    </xsl:otherwise>
                </xsl:choose>
                <xsl:if test="not(ancestor::amend) and label!='' ">
                <xsl:attribute name="data-location-breadcrumb">part <xsl:value-of select="label"/><xsl:text> </xsl:text></xsl:attribute>
                </xsl:if>

            <h2 class="part">
                <xsl:if test="label!='' ">
                    <span class="label"><xsl:if test="not(contains(label, 'Part'))">Part </xsl:if><xsl:value-of select="label"/></span>
                </xsl:if>
                <xsl:value-of select="heading"/>
            </h2>
            <xsl:apply-templates />
        </div>
    </xsl:template>

    <xsl:template match="part/label|part/heading">
    </xsl:template>


    <xsl:template match="subpart">
        <div class="subpart">
             <xsl:attribute name="id">
                <xsl:value-of select="@id"/>
            </xsl:attribute>
                <xsl:if test="@data-hook!=''">
                    <xsl:attribute name="data-hook">
                        <xsl:value-of select="@data-hook"/>
                    </xsl:attribute>
                    <xsl:attribute name="data-hook-length">
                        <xsl:value-of select="@data-hook-length"/>
                    </xsl:attribute>
                </xsl:if>
            <xsl:call-template name="current">
                <xsl:with-param name="class">subpart</xsl:with-param>
            </xsl:call-template>
                <xsl:attribute name="data-location-no-path"></xsl:attribute>
                <xsl:choose>
                     <xsl:when test="ancestor::*[@quote]  or ancestor::amend">
                     </xsl:when>
                    <xsl:when test="ancestor::schedule">
                        <xsl:attribute name="data-location">, cl <xsl:value-of select="normalize-space(./prov/label)"/></xsl:attribute>
                    </xsl:when>
                        <xsl:otherwise>
                        <xsl:attribute name="data-location">s <xsl:value-of select="normalize-space(./prov/label)"/></xsl:attribute>
                    </xsl:otherwise>
                </xsl:choose>
                 <xsl:if test="not(ancestor::amend)">
                <xsl:attribute name="data-location-breadcrumb">subpart <xsl:value-of select="label"/><xsl:text> </xsl:text></xsl:attribute>
                </xsl:if>
            <h3 class="subpart">
                <span class="label">Subpart <xsl:value-of select="label"/></span><span class="suffix">—</span>
                <xsl:value-of select="heading"/>
            </h3>
            <xsl:if test="@deletion-status='repealed'">
            <span class="subpart deletion-status">[Repealed]</span>
            </xsl:if>
            <xsl:apply-templates />
        </div>
    </xsl:template>

    <xsl:template match="subpart/label|subpart/heading">
    </xsl:template>


    <xsl:template match="prov">
        <div class="prov">
            <xsl:attribute name="id">
                <xsl:value-of select="@id"/>
            </xsl:attribute>
                <xsl:if test="@data-hook!=''">
                    <xsl:attribute name="data-hook">
                        <xsl:value-of select="@data-hook"/>
                    </xsl:attribute>
                    <xsl:attribute name="data-hook-length">
                        <xsl:value-of select="@data-hook-length"/>
                    </xsl:attribute>
                </xsl:if>
            <xsl:choose>
                     <xsl:when test="ancestor::*[@quote] or ancestor::amend">
                     </xsl:when>
                <xsl:when test="ancestor::schedule">
                    <xsl:attribute name="data-location">, cl <xsl:value-of select="normalize-space(label)"/></xsl:attribute>
                </xsl:when>
                    <xsl:otherwise>
                    <xsl:attribute name="data-location">s <xsl:value-of select="normalize-space(label)"/></xsl:attribute>
                </xsl:otherwise>
            </xsl:choose>
            <xsl:call-template name="current">
                <xsl:with-param name="class">prov</xsl:with-param>
            </xsl:call-template>
            <xsl:if test="heading !=''">
                    <h5 class="prov">
                        <a class="focus-link">
                        <xsl:attribute name="href">/open_article/instrument/<xsl:value-of select="@id"/></xsl:attribute>
                        <span class="label">
                            <xsl:call-template name="parentquote"/>
                            <xsl:value-of select="label"/>
                        </span>
                        <xsl:value-of select="heading"/>
                        </a>
                    </h5>
            </xsl:if>

            <div class="prov-body">

                    <xsl:choose>
                        <xsl:when test="not(@deletion-status)">
                             <xsl:apply-templates select="prov.body/subprov|prov.body/para/list|prov.body/subprov.crosshead|prov.body/example"/>
                             <xsl:if test="prov.body/para/text != ''">
                                 <p class="headless label">
                                        <span class="label">
                                                <xsl:call-template name="parentquote"/>
                                                 <a class="focus-link">
                                                <xsl:value-of select="label"/>
                                                </a>
                                        </span>
                                         <xsl:value-of select="prov.body/para/text"/>
                                </p>
                                    <xsl:apply-templates select="prov.body/para/label-para"/>
                                    <xsl:apply-templates select="prov.body/notes/history/history-note"/>
                             </xsl:if>
                        </xsl:when>
                    <xsl:otherwise>
                        <span class="prov deletion-status">
                            <xsl:choose>
                                <xsl:when test="ancestor::act">
                                        [Repealed]
                                    </xsl:when>
                                    <xsl:otherwise>
                                        [Revoked]
                                </xsl:otherwise>
                                </xsl:choose>
                            </span>
                            <!-- error in Lawyers and Conveyancers Act (Lawyers: Conduct and Client Care) Rules 2008 chapter 15 -->
                            <!--<span class="deleted label-deleted">

                            </span> -->
                        </xsl:otherwise>
                    </xsl:choose>
                    <xsl:apply-templates select="def-para|prov.body/para/def-para" />
            </div>
            <xsl:apply-templates select="notes|cf|ird.aids"/>
        </div>
    </xsl:template>


    <xsl:template match='subprov'>
        <div class="subprov">
            <xsl:call-template name="current">
                <xsl:with-param name="class">subprov</xsl:with-param>
            </xsl:call-template>
            <xsl:if test="label != '' and not(ancestor::*[@quote]) and not(ancestor::amend)">
                <xsl:attribute name="data-location">
                    <xsl:call-template name="bracketlocation">
                        <xsl:with-param name="label"><xsl:value-of select="normalize-space(label)"/></xsl:with-param>
                    </xsl:call-template>
                 </xsl:attribute>
            </xsl:if>

            <xsl:apply-templates />
        </div>
    </xsl:template>


    <xsl:template match='prov.body/para/list'>
        <ul class="list">
            <xsl:call-template name="current">
                <xsl:with-param name="class">list</xsl:with-param>
            </xsl:call-template>
            <xsl:apply-templates select="item" />
        </ul>
    </xsl:template>

    <xsl:template match="label-para">
        <div class="label-para">
            <xsl:call-template name="current"/>

            <xsl:call-template name="current">
                <xsl:with-param name="class">label-para</xsl:with-param>
            </xsl:call-template>
                <xsl:if test="label != '' and not(ancestor::*[@quote]) and not(ancestor::amend)">
                    <xsl:attribute name="data-location">
                    <xsl:call-template name="bracketlocation">
                        <xsl:with-param name="label"><xsl:value-of select="normalize-space(label)"/></xsl:with-param>
                    </xsl:call-template>
                </xsl:attribute>
                </xsl:if>
                <!-- label will render first para/text, so must match others separately -->
                <xsl:apply-templates />

        </div>
    </xsl:template>


    <xsl:template match="def-para">
        <div class="def-para">
            <xsl:call-template name="current">
                <xsl:with-param name="class">def-para</xsl:with-param>
            </xsl:call-template>
             <xsl:attribute name="id">
                <xsl:value-of select="@id"/>
            </xsl:attribute>

                <xsl:call-template name="quote"/>
                <xsl:apply-templates />

            <xsl:if test="@deletion-status='repealed'">
                <p class="deleted para-deleted">[Repealed]</p>
            </xsl:if>
        </div>
    </xsl:template>

    <!-- can't be right
    <xsl:template match="amend">
        <div class="def-para">
             <xsl:attribute name="class">
                flush-left-margin-<xsl:value-of select="amend"/>
            </xsl:attribute>
            <blockquote class="text">
                  <xsl:attribute name="class">
                    amend amend-increment-<xsl:value-of select="increment"/>
                </xsl:attribute>
                 <xsl:apply-templates />
            </blockquote>
        </div>
    </xsl:template>-->

    <xsl:template match="amend">
        <div>
             <xsl:attribute name="class">
            <xsl:choose>
                <xsl:when test="@increment='1'">increment-1 amend</xsl:when>
                <xsl:when test="@increment='2'">increment-2 amend</xsl:when>
                <xsl:when test="@increment='3'">increment-2 amend</xsl:when>
                <xsl:otherwise>amend</xsl:otherwise>
            </xsl:choose>
            </xsl:attribute>
             <xsl:apply-templates />
        </div>
    </xsl:template>

    <xsl:template match="def-term">
        <dfn class="def-term">
            <xsl:attribute name="id">
                <xsl:value-of select="@id"/>
            </xsl:attribute>
            <xsl:if test="ancestor::def-para/para/text  and not(ancestor::amend)" >
                <xsl:attribute name="data-location">define: <xsl:value-of select="."/>
                </xsl:attribute>
                <xsl:attribute name="data-location-no-path">true</xsl:attribute>
            </xsl:if>
            <xsl:apply-templates/>
        </dfn>
    </xsl:template>

    <xsl:template match="subprov/label">
        <p class="subprov">
            <xsl:call-template name="current">
                <xsl:with-param name="subprov"></xsl:with-param>
            </xsl:call-template>
            <xsl:choose>
            <xsl:when test="text() != ''">
                <span class="label focus-link">
                     <xsl:call-template name="parentquote"/>
                     <xsl:call-template name="openbracket"/>
                     <xsl:value-of select="."/>
                     <xsl:call-template name="closebracket"/>
                </span>
            </xsl:when>
            <xsl:otherwise>
                <span class="label"></span>
            </xsl:otherwise>
        </xsl:choose>
        </p>
    </xsl:template>

    <xsl:template match="label-para/label">
        <h5 class="label-para">
            <span class="label focus-link">
             <xsl:call-template name="parentquote"/>
             <xsl:call-template name="openbracket"/>
             <xsl:value-of select="."/>
             <xsl:call-template name="closebracket"/>
            </span>
        </h5>
    </xsl:template>

    <xsl:template match="label-para.crosshead">
      <p class="label-para-crosshead"><xsl:apply-templates/>
  </p>
    </xsl:template>

    <!--
    <xsl:template match="label">
        <p class="labelled label">
            <xsl:call-template name="current">
                <xsl:with-param name="class">labelled label</xsl:with-param>
            </xsl:call-template>

            <xsl:if test="text() != ''">
                <span class="label focus-link">
                     <xsl:call-template name="parentquote"/>
                     <xsl:call-template name="openbracket"/>
                     <xsl:value-of select="."/>
                     <xsl:call-template name="closebracket"/>
                </span>
            </xsl:if>
            <xsl:choose>
                <xsl:when test="../para[1]/text[1] != ''">
                    <xsl:apply-templates select="../para[1]/text[1]"/>
                </xsl:when>
                <xsl:otherwise>
                    <span class="deleted label-deleted">[Repealed]</span>
                </xsl:otherwise>
            </xsl:choose>
        </p>
    </xsl:template>
    -->


    <xsl:template match="follow-text[@space-before='no']">
    </xsl:template>

    <xsl:template match='crosshead'>
        <h4 class="crosshead">
             <xsl:attribute name="id">
                <xsl:value-of select="@id"/>
            </xsl:attribute>
            <xsl:value-of select="."/>
            <xsl:if test="@deletion-status='repealed'">
            <span class="crosshead deletion-status">[Repealed]</span>
            </xsl:if>
        </h4>
    </xsl:template>


    <xsl:template match='subprov.crosshead'>
        <h6 class="subprov-crosshead">
             <xsl:apply-templates />
            <xsl:if test="@deletion-status='repealed'">
                <span class="crosshead deletion-status">[Repealed]</span>
            </xsl:if>
        </h6>
    </xsl:template>

    <xsl:template match='ird-crosshead'>
        <h4 class="ird-crosshead">
             <xsl:apply-templates />
            <xsl:if test="@deletion-status='repealed'">
                <span class="crosshead deletion-status">[Repealed]</span>
            </xsl:if>
        </h4>
    </xsl:template>

    <xsl:template match='example'>
        <div class="example">
            <xsl:apply-templates />
        </div>
    </xsl:template>

    <xsl:template match='example/heading'>
        <h6 class="heading">
            <xsl:apply-templates />
        </h6>
    </xsl:template>

   <xsl:template match="example/text">
        <p  class="text"><xsl:apply-templates select="para"/></p>
    </xsl:template>

    <xsl:template match="notes/history">
        <div class="history">
            <xsl:apply-templates/>
        </div>
    </xsl:template>

    <xsl:template match="notes/editorial-note">
    </xsl:template>

    <xsl:template match="notes/amends-note">
    </xsl:template>

    <xsl:template match="notes/history/history-note">
        <p class="history-note">
            <xsl:attribute name="id">
                <xsl:value-of select="@id"/>
            </xsl:attribute>
            <xsl:apply-templates/>
        </p>
    </xsl:template>

    <xsl:template match="readers-notes">
        <div class="readers-notes">
            <xsl:apply-templates/>
        </div>
    </xsl:template>

    <xsl:template match="cf">
        <p class="cf">Compare <xsl:apply-templates/></p>
    </xsl:template>

    <xsl:template match="ird.aids">
       <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="term.list">
        <p class="term-list">Defined in this Act:
            <xsl:apply-templates/>
    </p>
    </xsl:template>

    <xsl:template match="history-note/amended-provision">
        <span class="amended-provision"><xsl:apply-templates/></span>
    </xsl:template>

    <xsl:template match="history-note/amending-operation">
        <span class="amending-operation"><xsl:apply-templates/></span>
    </xsl:template>

    <xsl:template match="history-note/amendment-date">
        <span class="amendment-date"><xsl:apply-templates/></span>
    </xsl:template>


     <xsl:template match="history-note/amending-leg">
        <span class="amending-leg"><xsl:apply-templates/></span>
    </xsl:template>

    <xsl:template match="admended-provision|amending-operation">
        <xsl:value-of select="."/>
    </xsl:template>


    <xsl:template match="emphasis[@style='bold']">
        <xsl:variable name="length" select="string-length(preceding::text()[1])"/>
          <!--<xsl:if test="string-length(preceding::text()[1])">
                <xsl:if test="string-length(translate(substring(preceding::text()[1], $length), $symbols-skip-insert-space, '')) = 0 ">&#160;</xsl:if>
        </xsl:if>-->
        <strong><xsl:apply-templates/></strong>
    </xsl:template>

    <xsl:template match="emphasis[@style='italic']">
        <xsl:variable name="length" select="string-length(preceding::text()[1])"/>
          <!--<xsl:if test="string-length(preceding::text()[1])">
                <xsl:if test="string-length(translate(substring(preceding::text()[1], $length), $symbols-skip-insert-space, '')) != 0 ">&#160;</xsl:if>
        </xsl:if>-->
       <em><xsl:apply-templates/></em>
    </xsl:template>

    <xsl:template match="emphasis[@style='roman']">
       <span class="roman"><xsl:apply-templates/></span>
    </xsl:template>

   <xsl:template match="catalex-def">
        <a class="def-popover" href="#" tabindex="0" data-toggle="popover"  data-html="true">
            <xsl:attribute name="data-def-id">
               <xsl:value-of select="@def-ids"/>
            </xsl:attribute>
            <xsl:attribute name="data-def-ex-id">
               <xsl:value-of select="@def-ex-ids"/>
            </xsl:attribute>
             <xsl:attribute name="data-def-idx">
               <xsl:value-of select="@def-idx"/>
            </xsl:attribute>
             <xsl:attribute name="href">/open_definition/<xsl:value-of select="@def-ids"/>/<xsl:value-of select="@def-ex-ids"/></xsl:attribute>
            <xsl:apply-templates select="text()"/>
        </a>
    </xsl:template>

    <xsl:template match="*[@href]">
        <a>
            <xsl:attribute name="data-link-id"><xsl:value-of select="@link-id"/></xsl:attribute>
            <xsl:attribute name="data-href"><xsl:value-of select="@href"/>
            </xsl:attribute>
            <xsl:choose>
            <xsl:when test="local-name() = 'intref'">
                  <xsl:attribute name="href">/open_article/instrument/<xsl:value-of select="@href"/>
                </xsl:attribute>
                 <xsl:attribute name="class">internal_ref</xsl:attribute>
                 <xsl:attribute name="data-target-id"><xsl:value-of select="@href"/></xsl:attribute>
            </xsl:when>
            <xsl:when test="local-name() = 'extref'">
                  <xsl:attribute name="href">/open_article/instrument/<xsl:value-of select="@href"/>
                </xsl:attribute>
                 <xsl:attribute name="class">external_ref</xsl:attribute>
            </xsl:when>
            <xsl:when test="local-name() = 'extref'">
                  <xsl:attribute name="href">/open_article/instrument/<xsl:value-of select="@href"/>
                </xsl:attribute>
                 <xsl:attribute name="class">external_ref</xsl:attribute>
            </xsl:when>
            <xsl:when test="local-name() = 'amending-provision'">
                  <xsl:attribute name="href">/open_article/instrument/<xsl:value-of select="@href"/>
                </xsl:attribute>
                 <xsl:attribute name="class">amending-provision external_ref</xsl:attribute>
            </xsl:when>
            <xsl:when test="local-name() = 'term'">
                  <xsl:attribute name="href">/open_article/instrument/<xsl:value-of select="@href"/>
                </xsl:attribute>
                 <xsl:attribute name="class">term external_ref</xsl:attribute>
            </xsl:when>
            <xsl:otherwise>
                  <xsl:attribute name="href">/open_article/<xsl:value-of select="@href"/></xsl:attribute>
                 <xsl:attribute name="data-target-id"><xsl:value-of select="@target-id"/></xsl:attribute>
                 <xsl:if test="@location != ''">
                    <xsl:attribute name="data-location"><xsl:value-of select="@location"/></xsl:attribute>
                </xsl:if>
            </xsl:otherwise>
        </xsl:choose>
           <xsl:apply-templates  />
        </a>
    </xsl:template>

    <xsl:template match="atidlm:link">
        <a>
            <xsl:attribute name="data-link-id"><xsl:value-of select="@atidlm:xmlId"/></xsl:attribute>
            <xsl:attribute name="data-href"><xsl:value-of select="atidlm:resourcepair/@atidlm:targetXmlId"/>
            </xsl:attribute>
              <xsl:attribute name="href">/open_article/instrument/<xsl:value-of select="atidlm:resourcepair/@atidlm:targetXmlId"/>
            </xsl:attribute>
            <xsl:value-of select="atidlm:linkcontent"/>
        </a>
    </xsl:template>

    <xsl:template match="link">
        <a>
            <xsl:attribute name="data-link-id"><xsl:value-of select="@xmlId"/></xsl:attribute>
            <xsl:attribute name="data-href"><xsl:value-of select="resourcepair/@targetXmlId"/>
            </xsl:attribute>
              <xsl:attribute name="href">/open_article/instrument/<xsl:value-of select="resourcepair/@targetXmlId"/>
            </xsl:attribute>
            <xsl:value-of select="linkcontent"/>
        </a>
    </xsl:template>

   <!-- <xsl:template match="*[@current = 'true']">

        <xsl:attribute name="class">current
        </xsl:attribute>
          <xsl:apply-templates/>
    </xsl:template> -->

   <xsl:template match="insertwords">
         <xsl:apply-templates />
    </xsl:template>



   <xsl:template match="citation">
         <xsl:apply-templates />
    </xsl:template>



    <xsl:template match="text()">
        <xsl:value-of select="."/>
    </xsl:template>

    <xsl:template match="para">
        <xsl:if test="text[1][not(node())] and not(ancestor::readers-notes)">
        <span class="label-para deletion-status">[Repealed]</span>
    </xsl:if>
        <div class="para"><xsl:apply-templates /></div>
    </xsl:template>

    <xsl:template match="para/text">
        <p class="text">
            <xsl:apply-templates />
        </p>
    </xsl:template>



    <xsl:template match="conv">
      <div class="conv">
        <xsl:attribute name="id">
            <xsl:value-of select="@id"/>
        </xsl:attribute>
        <xsl:apply-templates select="conv.body"/>
      </div>
    </xsl:template>

    <xsl:template match="conv.body">
      <div class="conv-body">
        <xsl:attribute name="id">
            <xsl:value-of select="@id"/>
        </xsl:attribute>
        <xsl:apply-templates />
      </div>
    </xsl:template>

    <xsl:template match="head1">
      <div class="head1">
        <xsl:attribute name="id">
            <xsl:value-of select="@id"/>
        </xsl:attribute>
        <xsl:if test="label != '' and starts-with(label, 'Part ')">
            <xsl:variable name="part">
              <xsl:call-template name="string-replace-all">
                <xsl:with-param name="text" select="label" />
                <xsl:with-param name="replace" select="'Part '" />
                <xsl:with-param name="by" select="''" />
              </xsl:call-template>
          </xsl:variable>
               <xsl:attribute name="data-location">, part <xsl:value-of select="normalize-space($part)"/></xsl:attribute>
        </xsl:if>
            <h2 class="head1">
                 <xsl:if test="label != ''">
                <span class="label">
                    <xsl:apply-templates select="label"/>
                </span>
                </xsl:if>
                <xsl:apply-templates select="heading"/>
            </h2>
        <xsl:apply-templates select="prov|para|head2|head3|head4|head5|notes"/>
      </div>
    </xsl:template>

    <xsl:template match="head2">
      <div class="head4">
        <xsl:attribute name="id">
            <xsl:value-of select="@id"/>
        </xsl:attribute>
            <h2 class="head2">
                <xsl:value-of select="heading"/>
            </h2>
        <xsl:apply-templates select="prov|para|head3|head4|head5"/>
      </div>
    </xsl:template>

    <xsl:template match="head3">
      <div class="head4">
        <xsl:attribute name="id">
            <xsl:value-of select="@id"/>
        </xsl:attribute>
            <h3 class="head3">
                <xsl:value-of select="heading"/>
            </h3>
                <xsl:apply-templates select="prov|para|head4|head5"/>
      </div>
    </xsl:template>

    <xsl:template match="head4">
      <div class="head4">
        <xsl:attribute name="id">
            <xsl:value-of select="@id"/>
        </xsl:attribute>
            <h4 class="head4">
                <xsl:value-of select="heading"/>
            </h4>
                <xsl:apply-templates select="prov|para|head5"/>
      </div>
    </xsl:template>

    <xsl:template match="head5">
      <div class="head4">
        <xsl:attribute name="id">
            <xsl:value-of select="@id"/>
        </xsl:attribute>
            <h5 class="head5">
                <xsl:value-of select="heading"/>
            </h5>
          <xsl:apply-templates select="prov|para"/>
      </div>
    </xsl:template>

    <xsl:template match="brk">
        <br class="brk"/>
    </xsl:template>

    <xsl:template match="field[@fill]">
        <span></span>
    </xsl:template>

    <xsl:template match="list">
            <ul class="list">
             <xsl:apply-templates select="item"/>
        </ul>
    </xsl:template>

    <xsl:template match="list/item">
        <li class="bull">
            <p class="item">
                <xsl:apply-templates />
            </p>
        </li>
    </xsl:template>

    <xsl:template match="item/label">
        <p class="labelled item">
            <xsl:call-template name="current"/>
            <xsl:if test="text() != '' and text() != '•'">
                <span class="label">
                     <xsl:call-template name="parentquote"/>(<xsl:value-of select="."/>)
                </span>
            </xsl:if>
            <xsl:choose>
                <xsl:when test="../para/text != ''">

                </xsl:when>
                <xsl:otherwise>
                    <span class="deleted label-deleted">[Repealed]</span>
                </xsl:otherwise>
            </xsl:choose>
        </p>
    </xsl:template>


    <xsl:template match="variable-def[1]">

        <dl class="variable-list">
            <xsl:apply-templates />
            <xsl:for-each select="../variable-def[position() > 1]">
                <xsl:apply-templates />
            </xsl:for-each>
        </dl>

    </xsl:template>

    <xsl:template match="variable-def[position() > 1]">

    </xsl:template>


    <xsl:template match="variable-def/variable">
        <dt class="variable">
            <xsl:apply-templates />
        </dt>
    </xsl:template>

    <xsl:template match="variable-def/para">
        <dd class="variable-description">
            <div class="para">
                <xsl:apply-templates />
            </div>
        </dd>
    </xsl:template>

      <xsl:template match="empowering-prov">
        <p class="empowering-prov">
            <xsl:apply-templates />
        </p>
    </xsl:template>

    <!-- currently no footnotes -->
    <xsl:template match="footnote">

    </xsl:template>


</xsl:stylesheet>